from enum import Enum


class NodeStatuses(str, Enum):
    """Перечисления для статусов нод (узлов) дорожной карты"""
    PUBLISHED = "published"
    DRAFT = "draft"
    ARCHIVED = "archive"