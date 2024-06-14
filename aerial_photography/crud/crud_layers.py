from typing import List, Union
from sqlalchemy import select, and_
# from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from aerial_photography.crud.base import CRUDBase
from sqlalchemy import func
from aerial_photography.models.layers import Layers
from aerial_photography.schemas.layers import (
    LayersCreate,
    LayerUpdate)

from aerial_photography.utils.geometry import convert_str_to_wkb, convert_wkb_to_str
from geoalchemy2.elements import WKBElement


class CRUDLayers(
    CRUDBase[Layers, LayersCreate, LayerUpdate]):
    '''
    Класс, реализующий функционал CRUD для таблицы `layers`
    '''

    def create(self, db: Session, *, obj_in: LayersCreate) -> List[Layers]:
        obj_in_data = [jsonable_encoder(obj) for obj in obj_in.layers]
        for obj in obj_in_data:
            obj['polygon_coordinates'] = convert_str_to_wkb(obj['polygon_coordinates'])

        db_objs = [self.model(**data) for data in obj_in_data]
        db.add_all(db_objs)
        db.commit()

        for db_obj in db_objs:
            db.refresh(db_obj)
            db_obj.polygon_coordinates = convert_wkb_to_str(db_obj.polygon_coordinates)
        return db_objs
    #
    def update(
            self,
            db: Session,
            *,
            db_obj: Layers,
            obj_in: LayerUpdate
    ) -> Layers:
        # Проверка корректности переданного полигона
        # convert_wkb_to_str(db_obj.footprint)
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        if isinstance(db_obj.polygon_coordinates, WKBElement):
            db_obj.polygon_coordinates = convert_wkb_to_str(db_obj.polygon_coordinates)

        return db_obj

    def get(self, db: Session, id: int) -> Union[Layers, None]:
        result = db.scalars(select(self.model).filter(self.model.id == id).limit(1))
        result = [item for item in result]
        if len(result) == 0:
            return None

        if isinstance(result[0].polygon_coordinates, WKBElement):
            result[0].polygon_coordinates = convert_wkb_to_str(result[0].polygon_coordinates)

        return result[0]

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Layers]:
        result = db.scalars(select(self.model).offset(skip).limit(limit))
        result = [item for item in result]
        for ind in range(len(result)):
            result[ind].polygon_coordinates = convert_wkb_to_str(result[ind].polygon_coordinates)

        return result

    def get_by_faiss_id(self, db: Session, faiss_id: int) -> Union[Layers, None]:
        result = db.scalars(select(self.model).filter(self.model.faiss_id == faiss_id).limit(1))
        result = [item for item in result]
        if len(result) == 0:
            return None

        if isinstance(result[0].polygon_coordinates, WKBElement):
            result[0].polygon_coordinates = convert_wkb_to_str(result[0].polygon_coordinates)

        return result[0]

    def get_by_faiss_id_and_layout_name(self, db: Session, faiss_id: int, layout_name: str) -> Union[Layers, None]:
        result = db.scalars(select(self.model).filter(
            self.model.faiss_id == faiss_id,
            self.model.layout_name == layout_name
        ).limit(1))
        result = [item for item in result]
        if len(result) == 0:
            return None

        if isinstance(result[0].polygon_coordinates, WKBElement):
            result[0].polygon_coordinates = convert_wkb_to_str(result[0].polygon_coordinates)

        return result[0]


    def remove(self, db: Session, *, id: int) -> Union[Layers, None]:
        obj = self.get(db=db, id=id)
        if obj is None:
            return None

        db.delete(obj)
        db.commit()
        return obj

    def get_count(self, db: Session):
        counts = db.query(func.count(self.model.id)).scalar()
        return counts


layer = CRUDLayers(Layers)
