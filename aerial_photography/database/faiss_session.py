from aerial_photography.database.faiss_interface import FAISS
from aerial_photography.config import faiss_config
import logging

logger = logging.getLogger("uvicorn.error")
db_faiss = FAISS(faiss_config)
try:
    db_faiss.load()
    logger.info(f'Индекс FAISS успешно загружен!')
except Exception as e:
    logger.warning(f'Не удалось загрузить FAISS index. Ошибка: {e}')
    db_faiss = None
