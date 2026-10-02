# infrastructure/uploaders.py

import os
import uuid

from django.utils import timezone
from django.utils.text import get_valid_filename


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


# ─────────────────────────────────────────────────────
# Общий хелпер
# ─────────────────────────────────────────────────────

def _build_image_path(
    filename: str,
    *prefixes: str,
    by_date: bool = True,
) -> str:
    """Формирует безопасный путь для загружаемого изображения.

    Args:
        filename: оригинальное имя файла.
        *prefixes: сегменты пути (например, "roadmap", "images").
        by_date: добавлять ли разбивку по дате (YYYY/MM/DD).

    Returns:
        Относительный путь внутри MEDIA_ROOT.
    """
    # 1. Отсекаем директории
    filename = os.path.basename(filename)

    # 2. Санитайзим
    filename = get_valid_filename(filename)

    # 3. Безопасное расширение
    _, dot, ext = filename.rpartition(".")
    ext = ext.lower() if dot else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = "bin"

    # 4. Уникальное имя
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    # 5. Собираем путь
    parts = list(prefixes)
    if by_date:
        today = timezone.now()
        parts.append(today.strftime("%Y/%m/%d"))
    parts.append(unique_name)

    return os.path.join(*parts)


# ─────────────────────────────────────────────────────
# Обёртки для конкретных полей
# ─────────────────────────────────────────────────────

def node_background_upload_to(instance, filename: str) -> str:
    """Путь для фонового изображения узла.

    Пример: roadmap/images/2026/09/11/3f2a1b4c8d9e.jpg
    """
    return _build_image_path(filename, "roadmap", "images")


def shard_image_upload_to(instance, filename: str) -> str:
    """Путь для изображения осколка карты.

    Пример: shards/2026/09/11/3f2a1b4c8d9e.jpg
    """
    return _build_image_path(filename, "shards")