from typing import Union, Iterable, List, Tuple, ByteString
from pydantic import BaseModel
from sqlalchemy import LargeBinary
from datetime import datetime

class Task(BaseModel):
    '''Схема модели в БД'''
    # faiss_id: int
    layout_name: str
    crop_name: str
    polygon_coordinates: str
    crs: str
    start_time: datetime



class TaskCreate(Task):
    pass


class TaskUpdate(Task):
    id: int


class TaskSchema(BaseModel):
    '''Схема задачи'''
    layout_name: str
    crop_name: str
    polygon_coordinates: str
    crs: str
    start_time: datetime


class TaskCreateSchema(TaskSchema):
    pass


class TaskUpdateSchema(TaskSchema):
    pass


# class LayersDeleteSchema(BaseModel):
#     ids: List[int]
