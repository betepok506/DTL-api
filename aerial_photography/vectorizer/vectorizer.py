from aerial_photography.utils.vectorizer import ImageVectorizer
from aerial_photography.config import settings
import torch
import logging

logger = logging.getLogger("uvicorn.error")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    image_vectorizer = ImageVectorizer(path_to_weight=settings.PATH_TO_WEIGHTS_VECTORIZER,
                                       name_model=settings.NAME_MODEL)
    logger.info(
        f'Модель успешно загружена! Имя модели: {settings.NAME_MODEL} Путь до весов: {settings.PATH_TO_WEIGHTS_VECTORIZER}')
except Exception as e:
    image_vectorizer = None
    logger.warning(f'Не удалось загрузить векторизатор. Ошибка: {e}')
