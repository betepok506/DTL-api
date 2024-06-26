'''
Данный модуль содержит вспомогательные функции для работы с геометрией
'''
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from typing import List, Tuple
import shapely
import shapely.wkt
import shapely.wkb
from shapely.geometry import mapping
from geoalchemy2.elements import WKBElement
from shapely.geometry import Polygon
from pyproj import Transformer
from shapely.ops import transform


def transform_polygon(polygon: Polygon, from_crs: str, to_crs: str) -> Polygon:
    # Создание трансформера для преобразования координат
    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)

    # Функция для преобразования координат
    def transform_coords(x, y):
        return transformer.transform(x, y)

    # Преобразование координат полигона
    transformed_polygon = transform(transform_coords, polygon)

    return transformed_polygon


def convert_polygon_to_str(polygon_coordinates: List[Tuple[float, float]]):
    '''
    Функция производит преобразование географических координат в wkb формат

    Parameter
    ----------
    polygon_coordinates: `List[List[int, int]]`
        Массив координат полигона

    Returns
    ----------
        `str` полигон, преобразованный в wkb формат
    '''
    polygon = Polygon(polygon_coordinates)
    return str(polygon)


def convert_str_to_wkb(str_polygon: str) -> WKBElement:
    wkb_format = from_shape(shapely.wkt.loads(str_polygon), 4326)
    return wkb_format


def convert_wkb_to_str(wkb: WKBElement) -> str:
    return str(to_shape(wkb))


def convert_wkb_to_coordinates(wkb: WKBElement):
    geom = shapely.wkb.loads(wkb)

    # Получение координат углов
    coords = list(mapping(geom)['coordinates'][0])

    # Упрощение координат до углов (верхний левый, верхний правый, нижний правый, нижний левый)
    ul, ur, br, bl = coords[0], coords[1], coords[2], coords[3]

    return ul, ur, br, bl
