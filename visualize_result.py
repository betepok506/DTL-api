import os
from shapely.geometry import Polygon
import rasterio
import httpx
from pathlib import Path
import io
from rasterio.plot import show
import asyncio
import cv2
import numpy as np
from utils_visualize import read_image, get_distance, normalize, transform_polygon

# PATH_TO_FILES = 'D://projects_andrey//hackaton//data_processing//data//crop//crop_50x50//layout_2021-10-10_downscale_50x50_crop'
PATH_TO_FILES = 'D://projects_andrey//hackaton//data//18. Sitronics//1_20'
RETURN_POLYGON = True
NORMALIZE = True  # True если надо нормализовать изображения


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
            polygon = Polygon([
                (upper_left[0], upper_left[1]),
                (lower_right[0], upper_left[1]),
                (lower_right[0], lower_right[1]),
                (upper_left[0], lower_right[1])
            ])
            return image_data, polygon
        return image_data, None


async def send_file(file_path, layout_name, url):
    filename = Path(file_path)
    with rasterio.open(file_path) as src:
        data = src.read()
        profile = src.profile

        img_byte_array = io.BytesIO()
        # profile.update(count=3)
        with rasterio.open(img_byte_array, 'w', **profile) as dst:
            dst.write(data)

        _, polygon = read_image(file_path, RETURN_POLYGON, NORMALIZE)

        img_byte_array.seek(0)
        files = {'file': (filename.name, img_byte_array, 'image/tiff')}
        payload = {'layout_name': layout_name}
        # Отправка POST запроса
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=payload, files=files, timeout=60)

            # Проверка статуса ответа
            if response.status_code == 200:
                # print('Файл успешно отправлен!')
                response = response.json()
                task_id = response['task_id']
                if task_id == -1:
                    print(f'Координаты для изображения: {filename} не найдены!')
                    return

                params = {'id': task_id}
                response = await client.get('http://localhost:8000/api/v1/tasks/', params=params)
                response.raise_for_status()  # Проверяет, был ли запрос успешным
                data = response.json()  # Предполагается, что ответ в формате JSON
                ul_predict = data['ul']
                ur_predict = data['ur']
                br_predict = data['br']
                bl_predict = data['bl']
                print(data)
                return ul_predict, br_predict
            else:
                print(f'Ошибка при отправке файла. Статус: {response.status_code}')
                print('Тело ответа:', response.text)




def geo_to_pixel(geo_coords, transform):
    lon, lat = geo_coords
    px, py = ~transform * (lon, lat)
    return int(px), int(py)


def draw_bboxes(image, bboxes, color=(255, 0, 0)):
    for idx, (bbox_true, bbox_predict) in enumerate(bboxes):
        x, y = bbox_true
        cv2.rectangle(image, (abs(x[0]), abs(x[1])), (abs(y[0]), abs(y[1])), color,
                      50)  # Зеленый bbox с толщиной линии 2
        true_center_x = x[0]+(y[0]-x[0])//2
        true_center_y = x[1]+(y[1]-x[1])//2

        x, y = bbox_predict
        cv2.rectangle(image, (abs(x[0]), abs(x[1])), (abs(y[0]), abs(y[1])), (0,0,255),
                      50)  # Зеленый bbox с толщиной линии 2
        predict_center_x = x[0] + (y[0] - x[0]) // 2
        predict_center_y = x[1] + (y[1] - x[1]) // 2
        cv2.arrowedLine(image, (true_center_x, true_center_y), (predict_center_x, predict_center_y), (255,255,255), 15)
        # cv2.putText(image, str(idx), (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 15, color, 50, cv2.LINE_AA)
    return image


def get_image_corners(transform, width, height):
    corners = {
        'top_left': (transform * (0, 0)),
        'top_right': (transform * (width, 0)),
        'bottom_left': (transform * (0, height)),
        'bottom_right': (transform * (width, height))
    }
    return corners


if __name__ == "__main__":
    # Загрузите исходное изображение Sentinel с помощью rasterio
    sentinel_image_path = 'D:\\projects_andrey\\hackaton\\data_processing\\data\\layout_2021-10-10.tif'
    with rasterio.open(sentinel_image_path) as dataset:
        transform = dataset.transform
        width = dataset.width
        height = dataset.height

        image = dataset.read([1, 2, 3])  # Чтение RGB каналов
        image = np.dstack(image)  # Объединение каналов в одно изображение
        image = normalize(image)

    corners = get_image_corners(transform, width, height)
    print("Координаты углов изображения (в географических координатах):")
    for corner_name, corner_coords in corners.items():
        print(f"{corner_name}: {corner_coords}")

    pixel_bboxes = []
    pixel_predict_bboxes = []
    for file_path in os.listdir(PATH_TO_FILES):
        file_path = os.path.join(PATH_TO_FILES, file_path)
        _, polygon = read_image(file_path, RETURN_POLYGON, NORMALIZE)
        # polygon_4326_true = transform_polygon(polygon, "EPSG:32637", "EPSG:4326")
        # polygon_32637_true = transform_polygon(polygon_4326_true, "EPSG:4326", "EPSG:32637")
        if not polygon is None:
            minx, miny, maxx, maxy = polygon.bounds
            ul_true, br_true = (minx, miny), (maxx, maxy)
            ul_true = geo_to_pixel(ul_true, transform)
            br_true = geo_to_pixel(br_true, transform)
            # Преобразование географических координат bbox в координаты пикселей
            pixel_bboxes.append((ul_true, br_true))
        else:
            pixel_bboxes.append(((0,0), (0,0)))
        predict = asyncio.run(send_file(file_path, 'layout_2022-03-17', 'http://localhost:8000/api/v1/tasks/'))
        if predict is None:
            print(f'Пропускаю изображение')
            continue

        (minx, miny), (maxx, maxy) = predict[0], predict[1]
        polygon_32637 = transform_polygon(Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)]),
                                          "EPSG:4326", "EPSG:32637"
                                          )
        minx_predict, miny_predict, maxx_predict, maxy_predict = polygon_32637.bounds
        ul_predict, br_predict = (int(minx_predict), int(miny_predict)), (int(maxx_predict), int(maxy_predict))
        ul_predict = geo_to_pixel(ul_predict, transform)
        br_predict = geo_to_pixel(br_predict, transform)
        pixel_predict_bboxes.append((ul_predict, br_predict))

    # Нарисовать bounding boxes на изображении
    image_with_bboxes = draw_bboxes(image.copy(), zip(pixel_bboxes, pixel_predict_bboxes), color=(255,0,0))
    # image_with_bboxes = draw_bboxes(image_with_bboxes.copy(), pixel_predict_bboxes, color=(0,0,255))

    # Отобразить изображение с bounding boxes
    # cv2.imshow('Image with Bboxes', image_with_bboxes)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Сохранить результат в файл
    cv2.imwrite('output_image_with_bboxes.jpg', image_with_bboxes)
