import os
import uuid

from django.utils import timezone
from django.utils.text import get_valid_filename

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def node_background_upload_to(instance, filename: str) -> str:
    """
    Формирует путь для фонового изображения узла.

    Пример результата:
        roadmap/images/2026/09/11/3f2a1b4c8d9e.jpg
    """
    # 1. Отсекаем любые директории из имени
    filename = os.path.basename(filename)

    # 2. Санитайзим имя (убирает пробелы, спецсимволы, control chars)
    filename = get_valid_filename(filename)

    # 3. Безопасно извлекаем расширение
    _, dot, ext = filename.rpartition(".")
    ext = ext.lower() if dot else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = "bin"

    # 4. Дата через strftime (с ведущими нулями)
    today = timezone.now()
    date_path = today.strftime("%Y/%m/%d")

    # 5. Уникальное имя
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    return os.path.join("roadmap", "images", date_path, unique_name)