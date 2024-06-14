import os

import httpx
import asyncio


# Асинхронная функция для отправки файла
async def send_file(file_path, url):
    # Имя файла
    filename = file_path.split('/')[-1]
    layout_name = 'layout_2021-06-15'
    # Формирование payload и files
    payload = {'layout_name': layout_name}
    with open(file_path, 'rb') as file:
        files = {'file': (filename, file.read(), 'image/tiff')}

        # Отправка POST запроса
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=payload, files=files, timeout=10)

            # Проверка статуса ответа
            if response.status_code == 200:
                print('Файл успешно отправлен!')
            else:
                print(f'Ошибка при отправке файла. Статус: {response.status_code}')
                print('Тело ответа:', response.text)


# Основная асинхронная функция
async def main():
    # file_path = 'data/layout_2021-06-15_crop_256x256_0_0.tif'
    for filename in os.listdir('./data'):
        url = 'http://localhost:8000/api/v1/tasks/'
        await send_file(os.path.join('./data', filename), url)


# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())