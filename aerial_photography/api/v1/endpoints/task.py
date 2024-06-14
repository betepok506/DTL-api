import io

from sqlalchemy.orm import Session
import numpy as np
from PIL import Image
from fastapi import APIRouter, UploadFile, File,Query, Depends, HTTPException, Form
from aerial_photography.api.deps import get_db_session
from aerial_photography import schemas
from aerial_photography import crud
from datetime import datetime

from aerial_photography.utils.geometry import convert_wkb_to_coordinates
from aerial_photography.vectorizer.vectorizer import image_vectorizer
from aerial_photography.database.faiss_session import db_faiss
from aerial_photography.utils.nms import apply_nms
import imghdr
router = APIRouter()


@router.post("/tasks/")
async def process_image(layout_name: str = Query(...),
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db_session)):
    # TODO отследить время
    tt = file.filename
    image_data = await file.read()
    with open('ttt.tif', "wb") as f:
        f.write(image_data)

    # with open('ttt.tif', "rb") as f:
    image = Image.open('ttt.tif')

    # image_format = imghdr.what(None, h=image_data)
    # image_stream = io.BytesIO(image_data)
    # # image = Image.open(io.BytesIO(image_data))
    # image = Image.open(image_stream)
    image_vector = image_vectorizer.vectorize(image)

    # Поиск ближайших соседей в FAISS
    #TODO получение индексов из faiss
    # index =
    distances, indices = db_faiss.search(np.array([image_vector]), k=5)

    # Получение информации из базы данных
    results = []
    for idx in indices[0]:
        result = crud.layer.get_by_faiss_id_and_layout_name(db=db, faiss_id=idx, layout_name=layout_name)
        if result:
            results.append(result)

    filtered_results = apply_nms(results)

    # TODO сохранить результат

    # return {"task_id": task.id}


@router.post("/tasks/result/")
async def get_task(task_id: int = Form(...), db: Session = Depends(get_db_session)):
    task = crud.task.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    ul, ur, br, bl = convert_wkb_to_coordinates(task.coordinates)

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
