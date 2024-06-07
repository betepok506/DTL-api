import logging
import os
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    """App settings."""

    API_V1_STR: str = "/api/v1"

    PROJECT_NAME: str = "aerial-photography-server"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"

    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", 'postgres')
    DATABASE_PORT: str = os.getenv('DATABASE_PORT', '6503')
    DATABASE_URI: str = os.getenv('DATABASE_URI', 'localhost') + ":" + DATABASE_PORT
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'postgres')
    # SQLALCHEMY_DATABASE_URL: str = f"postgresql+asyncpg://postgres:postgres@{DATABASE_URI}/{POSTGRES_PASSWORD}"
    SQLALCHEMY_DATABASE_URL: str = f"postgresql://postgres:postgres@{DATABASE_URI}/{POSTGRES_PASSWORD}"

    # Database
    DATABASE_URL: str = SQLALCHEMY_DATABASE_URL

    class ConfigDict:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
