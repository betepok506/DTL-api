from aerial_photography.database.base_class import Base
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    ARRAY,
    Integer,
    DateTime,
    ForeignKey, String
)
from sqlalchemy.orm import relationship


class Layers(Base):
    __tablename__ = "layers"

    id = Column('id', Integer, primary_key=True)
    faiss_id = Column('faiss_id', Integer)

    layout_name = Column("layout_name", String)

    dim_space_x = Column("dim_space_x", Integer)
    dim_space_y = Column("dim_space_y", Integer)
    polygon_coordinates = Column('polygon_coordinates', Geometry('POLYGON'))  # Координаты полигона, в котором будут запрашиваться снимки
    filename = Column("filename", String)

    created_at = Column("created_at", DateTime(timezone=True), default=func.now())