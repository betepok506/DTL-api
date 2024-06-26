import logging
import os
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)


class FAISSConfig:
    '''Данный класс содержит параметры конфигурации для работы с FAISS'''
    path_to_index: str = os.getenv("PATH_TO_FAISS_INDEX", '../dependencies/db_faiss')  # Путь до папки, где хранятся индексы
    path_to_block_index: str = f'{path_to_index}/block'  # Путь до папки, содержищей блоки индекса
    name_index: str = 'faiss_index.index'  # Название файла, содержащего индекс
    trained_index: str = 'trained_index.index'  # Название файла, содержащего индекс для тренировки

    vector_dim: int = int(os.getenv('VECTOR_DIM'))  # Размер вектора
    num_clusters: int = int(os.getenv('NUM_CLUSTERS'))  # Количество векторов
    block_size: int = 1024  # Количество векторов в одном блоке

    overwriting_indexes = False  # True если удалять ранее созданный индекс


class Settings(BaseSettings):
    """App settings."""

    API_V1_STR: str = "/api/v1"

    PROJECT_NAME: str = "aerial-photography-server"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"

    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", 'postgres')
    DATABASE_PORT: str = os.getenv('DATABASE_PORT', '5432')
    DATABASE_URI: str = os.getenv('DATABASE_URI', 'localhost') + ":" + DATABASE_PORT
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'postgres')
    NAME_MODEL: str = os.getenv("NAME_MODEL")
    # SQLALCHEMY_DATABASE_URL: str = f"postgresql+asyncpg://postgres:postgres@{DATABASE_URI}/{POSTGRES_PASSWORD}"
    SQLALCHEMY_DATABASE_URL: str = f"postgresql://postgres:postgres@{DATABASE_URI}/{POSTGRES_PASSWORD}"

    PATH_TO_WEIGHTS_VECTORIZER: str = os.getenv('PATH_TO_WEIGHTS_VECTORIZER', '../dependencies/weights/resnet50_2_cosine_sim_cos.pth')# '/dependencies/weights/resnet50_3.pth'
    PATH_TO_FAISS_INDEX: str = os.getenv("PATH_TO_FAISS_INDEX", '../dependencies/db_faiss')
    # Database
    DATABASE_URL: str = SQLALCHEMY_DATABASE_URL

    class ConfigDict:
        env_file = ".env"
        case_sensitive = True


faiss_config = FAISSConfig()
settings = Settings()
