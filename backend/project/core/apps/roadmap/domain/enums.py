from enum import Enum


class NodeStatuses(str, Enum):
    """Перечисления для статусов нод (узлов) дорожной карты"""
    PUBLISHED = "Активный"
    DRAFT = "Редактируется"
    ARCHIVED = "Архивный"