import io
import rasterio
from sqlalchemy.orm import Session
import numpy as np
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Query, Depends, HTTPException, Form
from aerial_photography.api.deps import get_db_session
from aerial_photography import schemas
from aerial_photography import crud
from datetime import datetime
from shapely import wkt, Polygon

from shapely.ops import transform as shapely_transform
from pyproj import Proj, Transformer

from aerial_photography.utils.vectorizer import normalize
from aerial_photography.utils.geometry import convert_wkb_to_coordinates, transform_polygon, convert_polygon_to_str
from aerial_photography.vectorizer.vectorizer import image_vectorizer, device
from aerial_photography.database.faiss_session import db_faiss
from aerial_photography.utils.nms import apply_nms
from aerial_photography.schemas.tasks import TaskCreate
# from aerial_photography.utils.geometry import transform_polygon
import imghdr

router = APIRouter()


@router.post("/tasks/")
async def process_image(layout_name: str = Query(...),
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db_session)):
    start_time = datetime.now()

    image_data = await file.read()
    img_byte_array = io.BytesIO(image_data)
    with rasterio.open(img_byte_array) as src:
        image = src.read()
        profile = src.profile

    max_value = np.max(image)
    # Если изображение не нормированно, то нормируем его
    image = image[:3].transpose((1, 2, 0))
    if max_value > 255:
        image = normalize(image)

    if image_vectorizer is None:
        raise HTTPException(status_code=500, detail=f"The Neural Network is not loaded. Contact the administrator")
    image_vector = image_vectorizer.vectorize(image)

    # Поиск ближайших соседей в FAISS
    if db_faiss is None:
        raise HTTPException(status_code=500, detail=f"The FAISS database is not loaded. Contact the administrator")

    distances, indices = db_faiss.search(image_vector, k=100)

    # Получение информации из базы данных
    bounding_boxes = []
    scores = []
    info = []
    for ind, idx in enumerate(indices[0]):
        result = crud.layer.get_by_faiss_id_and_layout_name(db=db, faiss_id=int(idx), layout_name=layout_name)
        if result:
            polygon = wkt.loads(result.polygon_coordinates)
            # polygon = transform_polygon(polygon, "EPSG:32637", "EPSG:4326")
            minx, miny, maxx, maxy = polygon.bounds
            bounding_boxes.append([minx, miny, maxx, maxy])
            scores.append(distances[0][ind])
            info.append({"filename": result.filename})
            # bboxes.append(result)
    if len(bounding_boxes) == 0:
        return {"task_id": -1}

    filtered_results = apply_nms(bounding_boxes, scores)
    minx, miny, maxx, maxy = filtered_results
    task_scheme = TaskCreate(layout_name=layout_name,
                             crop_name=file.filename,
                             polygon_coordinates=str(
                                 Polygon([(minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny), (minx, maxy)])),
                             crs='EPSG:4326',
                             start_time=start_time)
    task = crud.task.create(db=db, obj_in=task_scheme)
    return {"task_id": task.id}


@router.get("/tasks/")
async def get_task(*,
                   db: Session = Depends(get_db_session),
                   id: int):
    task = crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    polygon = wkt.loads(task.polygon_coordinates)
    minx, miny, maxx, maxy = polygon.bounds
    ul, ur, br, bl = (minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny) #convert_wkb_to_coordinates(task.coordinates)

    return {
        "id": task.id,
        "layout_name": task.layout_name,
        "crop_name": task.crop_name,
        "ul": ul,
        "ur": ur,
        "br": br,
        "bl": bl,
        "crs": task.crs,
        "start": task.start_time,
        "end": task.end_time
    }
