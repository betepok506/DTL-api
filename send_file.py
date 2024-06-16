import os
from PIL import Image
import io
import httpx
import asyncio
import rasterio
from pathlib import Path
from shapely.geometry import Polygon
from pyproj import Transformer
from shapely.ops import transform
from pyproj import Geod
import numpy as np

PATH_TO_FILES = 'D://Hackaton//DTL-data-processing//data//crop//crop_10x10//layout_2021-10-10_crop'
global_mean_dist = []


def transform_polygon(polygon: Polygon, from_crs: str, to_crs: str) -> Polygon:
    # Создание трансформера для преобразования координат
    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)

    # Функция для преобразования координат
    def transform_coords(x, y):
        return transformer.transform(x, y)

    # Преобразование координат полигона
    transformed_polygon = transform(transform_coords, polygon)

    return transformed_polygon


def read_image(path_to_image: str):
    '''Функция для чтения изображения и извлечения координат углов'''

    with rasterio.open(path_to_image) as dataset:
        # Чтение данных изображения
        image_data = dataset.read()

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


def get_distance(point_true, point_predict):
    geod = Geod(ellps='WGS84')
    lon1, lat1 = point_true
    lon2, lat2 = point_predict

    # Вычисление расстояния между координатами
    _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
    return distance


# Асинхронная функция для отправки файла
async def send_file(file_path, url):
    # Имя файла
    filename = Path(file_path)

    layout_name = filename.name.split('_')
    layout_name = '_'.join(layout_name[:2])
    # Формирование payload и files
    payload = {'layout_name': layout_name}
    global global_mean_dist

    with rasterio.open(file_path) as src:
        data = src.read()
        profile = src.profile

        img_byte_array = io.BytesIO()
        with rasterio.open(img_byte_array, 'w', **profile) as dst:
            dst.write(data)
        _, polygon = read_image(file_path)
        # bounds = polygon.bounds
        minx, miny, maxx, maxy = polygon.bounds
        ul_true, ur_true, br_true, bl_true = (minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny)

        img_byte_array.seek(0)
        files = {'file': (filename.name, img_byte_array, 'image/tiff')}

        # Отправка POST запроса
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=payload, files=files, timeout=60)

            # Проверка статуса ответа
            if response.status_code == 200:
                print('Файл успешно отправлен!')
                response = response.json()
                task_id = response['task_id']
                if task_id == -1:
                    return

                params = {'id': task_id}
                response = await client.get('http://localhost:8000/api/v1/tasks/', params=params)
                response.raise_for_status()  # Проверяет, был ли запрос успешным
                data = response.json()  # Предполагается, что ответ в формате JSON
                ul_predict = data['ul']
                ur_predict = data['ur']
                br_predict = data['br']
                bl_predict = data['bl']
                mean_dist = []
                for point_predict, point_true in zip([ul_predict, ur_predict, br_predict, bl_predict],
                                                     [ul_true, ur_true, br_true, bl_true]):
                    mean_dist.append(get_distance(point_true, point_predict))
                print(f'Дистанция: {np.mean(mean_dist)}')
                global_mean_dist.append(np.mean(mean_dist))
            else:
                print(f'Ошибка при отправке файла. Статус: {response.status_code}')
                print('Тело ответа:', response.text)


# Основная асинхронная функция
async def main():
    for filename in os.listdir(PATH_TO_FILES):
        url = 'http://localhost:8000/api/v1/tasks/'
        await send_file(os.path.join(PATH_TO_FILES, filename), url)

    print(f'Средняя ошибка по всем изображениям: {np.mean(global_mean_dist)}')
    print(f'Количество изобраений: {len(global_mean_dist)}')


# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
