FROM python:3.9-slim
ARG PORT=5000
EXPOSE $BACKEND_PORT
RUN echo "The application will run on port $BACKEND_PORT"

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY aerial_photography /app/aerial_photography

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD uvicorn aerial_photography.app:app --reload --workers 1 --host 0.0.0.0 --port $BACKEND_PORT