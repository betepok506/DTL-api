from shapely.geometry import Polygon
from pyproj import Transformer
from shapely.ops import transform
from pyproj import Geod
import rasterio
from datetime import datetime, timedelta
import pytz
import numpy as np


def transform_polygon(polygon: Polygon, from_crs: str, to_crs: str) -> Polygon:
    # Создание трансформера для преобразования координат
    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)

    # Функция для преобразования координат
    def transform_coords(x, y):
        return transformer.transform(x, y)

    # Преобразование координат полигона
    transformed_polygon = transform(transform_coords, polygon)

    return transformed_polygon


def get_distance(point_true, point_predict):
    geod = Geod(ellps='WGS84')
    lon1, lat1 = point_true
    lon2, lat2 = point_predict

    # Вычисление расстояния между координатами
    _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
    return distance


def normalize(image):
    # max_value = 4096
    image = np.log1p(image.astype(np.float32))
    min_value = np.min(image)
    max_value = np.max(image)
    # линейное преобразование для нормирования пикселей
    image = ((image - min_value) / (max_value - min_value)) * 255

    return image.astype(np.uint16)


def read_image(path_to_image: str, return_polygon: bool = False, is_normalize: bool = False):
    '''Функция для чтения изображения и извлечения координат углов'''

    with rasterio.open(path_to_image) as dataset:
        # Чтение данных изображения
        image_data = dataset.read()
        if is_normalize:
            image_data = normalize(image_data[:3].transpose((1, 2, 0)))

        if return_polygon:
            # Получение трансформации изображения
            transform = dataset.transform
            upper_left = (transform[2], transform[5])  # координаты левого верхнего угла
            lower_right = (transform[2] + transform[0] * dataset.width,  # X координата правого нижнего угла
                           transform[5] + transform[4] * dataset.height)
            polygon = transform_polygon(Polygon([
                (upper_left[0], upper_left[1]),
                (lower_right[0], upper_left[1]),
                (lower_right[0], lower_right[1]),
                (upper_left[0], lower_right[1])
            ]), "EPSG:32637", "EPSG:4326")

            return image_data, polygon
        else:
            return image_data, None


def convert_str_to_datetime(date_str, date_format):
    """
    Функция для преобразования строки в datetime объект.

    :param date_str: Дата и время в строковом формате.
    :param date_format: Формат строки с датой и временем.
    :return: Объект datetime.
    """
    return datetime.strptime(date_str, date_format)


def subtract_and_adjust_time_in_seconds(dt1_str, dt2_str, date_format="%Y-%m-%dT%H:%M:%S.%f"):
    """
    Функция для вычитания одного datetime из другого, вычитания 3 часов и преобразования в секунды.

    :param dt1: Первый datetime объект.
    :param dt2: Второй datetime объект.
    :return: Разница между dt1 и dt2 минус 3 часа в секундах.
    """

    dt1 = datetime.fromisoformat(dt1_str)
    dt2 = convert_str_to_datetime(dt2_str, date_format)
    dt1 = dt1.replace(tzinfo=None)
    # if dt2.tzinfo is None:
    #     dt2 = pytz.timezone('Europe/Moscow').localize(dt1)
    # Вычислить разницу между двумя datetime
    difference = dt1 - dt2

    # Вычесть 3 часа (timedelta(hours=3))
    adjusted_difference = difference - timedelta(hours=3)

    # Преобразовать результат в секунды
    result_in_seconds = adjusted_difference.total_seconds()

    return result_in_seconds
