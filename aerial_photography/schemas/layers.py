from typing import Union, Iterable, List, Tuple, ByteString
from pydantic import BaseModel
from sqlalchemy import LargeBinary


class Layer(BaseModel):
    '''Схема модели в БД'''
    faiss_id: int
    layout_name: str
    dim_space_x: int
    dim_space_y: int
    polygon_coordinates: str
    filename: str


class Layers(BaseModel):
    layers: List[Layer]


class LayersCreate(Layers):
    pass


class LayerUpdate(Layer):
    id: int


class LayerSchema(BaseModel):
    '''Схема подложки'''
    faiss_id: int
    layout_name: str
    dim_space_x: int
    dim_space_y: int
    polygon_coordinates: str
    filename: str


class LayersSchema(BaseModel):
    layers: List[LayerSchema]


class LayersCreateSchema(LayersSchema):
    pass


class LayersUpdateSchema(LayersSchema):
    pass


class LayersDeleteSchema(BaseModel):
    ids: List[int]
