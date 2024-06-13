from aerial_photography.database.faiss_interface import FAISS
from aerial_photography.config import faiss_config

db_faiss = FAISS(faiss_config)
try:
    db_faiss.load()
except Exception as e:
    print(f'Не удалось загрузить FAISS index')
    db_faiss = None
