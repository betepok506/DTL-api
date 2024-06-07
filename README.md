# 3. Запуск

# 3.1 Запуск

Конфигурирование сервера осуществляется с помощью `.env` файла.
Структура файла:

- `POSTGRES_USER` --- Имя пользователя
- `POSTGRES_PASSWORD` --- Пароль
- `POSTGRES_DB` --- Имя базы данных
- `DATABASE_URI` --- URI адрес базы данных в формате <HOST>:<PORT>

Для запуска сервера необходимо воспользоваться следующей командой:

```commandline
bash ./tools/run_server.sh
```

# Запуск Docker

Перед запуском контейнера необходимо создать сеть
```
docker network create network-aerial-photography
```
Запуск
```
docker-compose --env-file .env up --build
```

Для локального запуска необходимо установить все зависимости, выполнив команду:

```commandline
pip install -r requirements.txt
```