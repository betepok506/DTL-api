from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from shapely.errors import GEOSException
from sqlalchemy.exc import IntegrityError
from aerial_photography.api.deps import get_db_session
from aerial_photography import schemas
from aerial_photography import crud
import sqlalchemy

router = APIRouter()


@router.post("/layers")
def create_layers(
        *,
        db: Session = Depends(get_db_session),
        layers_in: schemas.LayersSchema
):
    '''
    "POLYGON ((44.680385 54.721345, 46.226831 54.781341, 46.306982 53.69887, 44.392784 53.77993, 44.680385 54.721345))"
    '''
    layers = crud.layer.create(db=db, obj_in=layers_in)
    return layers


#
@router.delete("/layer/{id}")
def delete_layer(
        *,
        db: Session = Depends(get_db_session),
        id: int
):
    removed_layer = crud.layer.remove(db=db, id=id)
    if not removed_layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    return removed_layer


@router.put("/layer")
def update_layer(
        *,
        db: Session = Depends(get_db_session),
        layer_in: schemas.LayerUpdate
):
    layer = crud.layer.get(db=db, id=layer_in.id)
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    updated_layer = crud.layer.update(db=db, db_obj=layer, obj_in=layer_in)

    return updated_layer


#
#
@router.get("/layer")
def get_layer(
        *,
        db: Session = Depends(get_db_session),
        id: int
):
    layer = crud.layer.get(db=db, id=id)
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    return layer


@router.get("/get_layer_by_faiss_id")
def get_layer(
        *,
        db: Session = Depends(get_db_session),
        faiss_id: int
):
    layer = crud.layer.get_by_faiss_id(db=db, faiss_id=faiss_id)
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    return layer


@router.get("/layers")
def get_layers(
        *,
        db: Session = Depends(get_db_session),
        skip: int = 0,
        limit: int = 100
):
    layers = crud.layer.get_multi(db=db, skip=skip, limit=limit)
    return {'layers': layers, 'counts': len(layers), 'limit': limit, "skip": skip}

#
# @router.post("/get_non_downloaded_polygons_to_search_for")
# def get_non_downloaded_polygons_to_search_for(
#         *,
#         db: Session = Depends(get_db_session),
#         data_in: schemas.PolygonsToSearchForSearchByPrograms
# ):
#     polygons = crud.polygons_to_search_for.search(db=db, obj_in=data_in)
#     if not polygons:
#         raise HTTPException(status_code=404, detail="Polygon not found")
#
#     return polygons
