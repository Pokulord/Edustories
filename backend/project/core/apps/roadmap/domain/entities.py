from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .enums import NodeStatuses


@dataclass(frozen=True)
class NodeRevision:
    """
    Ревизия узла. Immutable.
    Однажды созданная ревизия никогда не меняется.
    """
    uid: UUID
    node_id: UUID
    title: str
    task_text: str
    correct_answer: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_answer_correct(self, user_answer: str) -> bool:
        """Сверяет ответ"""
        return self.correct_answer.strip().lower() == user_answer.strip().lower()


@dataclass
class Node:
    """Сущность для узла дорожной карты"""

    uid: UUID = field(default_factory=uuid4)
    title: str
    order: int
    current_revision: NodeRevision | None = None
    status: NodeStatuses = NodeStatuses.DRAFT

    @property
    def is_published(self) -> bool:
        """Функция для проверки публикации узла"""
        return self.status == NodeStatuses.PUBLISHED

    def unpublish(self) -> None:
        """Переводит узел в статус неактивного"""
        self.status = NodeStatuses.DRAFT

    def archive(self) -> None:
        """Архивирует точку"""
        self.status = NodeStatuses.ARCHIVED

    def can_user_view(self) -> bool:
        """Отвечает за возможность просмотра точки студентом"""
        return self.is_published

    def can_user_answer(self) -> bool:
        """Отвечает за возможность ответа на вопросы точки"""
        return self.is_published


@dataclass
class Roadmap:
    """Сущность для дорожной карты"""
    uid: UUID = field(default_factory=uuid4)
    title: str
    points: list[Node] = field(default_factory=list)
