from aerial_photography.utils.vectorizer import ImageVectorizer
from aerial_photography.config import settings

try:
    image_vectorizer = ImageVectorizer(path_to_weight=settings.PATH_TO_WEIGHTS_VECTORIZER)
except Exception as e:
    image_vectorizer = None
    print(f'Не удалось загрузить векторизатор. Ошибка: {e}')
