'''
Данный модуль содержит вспомогательные функции для работы с геометрией
'''
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from typing import List, Tuple
import shapely
import shapely.wkt
from geoalchemy2.elements import WKBElement


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
