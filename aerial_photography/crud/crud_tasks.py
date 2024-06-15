from typing import List, Union
from sqlalchemy import select, and_
# from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from aerial_photography.crud.base import CRUDBase
from sqlalchemy import func
from aerial_photography.models.tasks import Tasks
from aerial_photography.schemas.tasks import (
    TaskCreate,
    TaskUpdate)

from aerial_photography.utils.geometry import convert_str_to_wkb, convert_wkb_to_str
from geoalchemy2.elements import WKBElement


class CRUDTasks(
    CRUDBase[Tasks, TaskCreate, TaskUpdate]):
    '''
    Класс, реализующий функционал CRUD для таблицы `layers`
    '''

    def create(self, db: Session, *, obj_in: TaskCreate) -> Tasks:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['polygon_coordinates'] = convert_str_to_wkb(obj_in_data['polygon_coordinates'])

        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        db_obj.polygon_coordinates = convert_wkb_to_str(db_obj.polygon_coordinates)
        #
        #
        # obj_in_data = [jsonable_encoder(obj) for obj in obj_in.layers]
        # for obj in obj_in_data:
        #     obj['polygon_coordinates'] = convert_str_to_wkb(obj['polygon_coordinates'])
        #
        # db_objs = [self.model(**data) for data in obj_in_data]
        # db.add_all(db_objs)
        # db.commit()
        #
        # for db_obj in db_objs:
        #     db.refresh(db_obj)
        #     db_obj.polygon_coordinates = convert_wkb_to_str(db_obj.polygon_coordinates)
        return db_obj

    #
    def update(
            self,
            db: Session,
            *,
            db_obj: Tasks,
            obj_in: TaskUpdate
    ) -> Tasks:
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

    def get(self, db: Session, id: int) -> Union[Tasks, None]:
        result = db.scalars(select(self.model).filter(self.model.id == id).limit(1))
        result = [item for item in result]
        if len(result) == 0:
            return None

        if isinstance(result[0].polygon_coordinates, WKBElement):
            result[0].polygon_coordinates = convert_wkb_to_str(result[0].polygon_coordinates)

        return result[0]


task = CRUDTasks(Tasks)
