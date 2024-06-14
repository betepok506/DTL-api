from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from shapely.errors import GEOSException
from sqlalchemy.exc import IntegrityError
from aerial_photography.api.deps import get_db_session
from aerial_photography import schemas
from aerial_photography import crud
import sqlalchemy
from aerial_photography.database.faiss_session import db_faiss



router = APIRouter()


@router.post("/findings_coordinates")
def findings_coordinates(
        *,
        db: Session = Depends(get_db_session),
        layers_in: schemas.LayersSchema
):
    '''
    "POLYGON ((44.680385 54.721345, 46.226831 54.781341, 46.306982 53.69887, 44.392784 53.77993, 44.680385 54.721345))"
    '''
    layers = crud.layer.create(db=db, obj_in=layers_in)
    return layers