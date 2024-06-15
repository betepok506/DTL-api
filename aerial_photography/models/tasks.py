from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String
)
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

from aerial_photography.database.base_class import Base


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column('id', Integer, primary_key=True, index=True)
    layout_name = Column('layout_name', String, index=True)
    crop_name = Column('crop_name', String, index=True)
    polygon_coordinates = Column('polygon_coordinates',
                                 Geometry('POLYGON'))  # Координаты полигона, в котором будут запрашиваться снимки
    crs = Column('crs', String)
    # result_ids = Column(String)  # Сохраняем идентификаторы результатов
    start_time = Column('start_time', DateTime)
    end_time = Column('end_time', DateTime(timezone=True), default=func.now())
