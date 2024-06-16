from aerial_photography.utils.vectorizer import ImageVectorizer
from aerial_photography.config import settings
import torch
import logging

logger = logging.getLogger("uvicorn.error")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    image_vectorizer = ImageVectorizer(path_to_weight=settings.PATH_TO_WEIGHTS_VECTORIZER)
    logger.info(f'Модель успешно загружена!')
except Exception as e:
    image_vectorizer = None
    logger.warning(f'Не удалось загрузить векторизатор. Ошибка: {e}')
