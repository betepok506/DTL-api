FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Установка временной зоны (например, Europe/London)
RUN ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    libomp-dev \
    libgfortran5 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Faiss через pip
RUN pip3 install --no-cache-dir faiss-cpu

ARG PORT=5000
EXPOSE $BACKEND_PORT
RUN echo "The application will run on port $BACKEND_PORT"
RUN pip3 install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 -f https://download.pytorch.org/whl/torch_stable.html

ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /app

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

COPY aerial_photography /app/aerial_photography

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD uvicorn aerial_photography.app:app --reload --workers 1 --host 0.0.0.0 --port $BACKEND_PORT