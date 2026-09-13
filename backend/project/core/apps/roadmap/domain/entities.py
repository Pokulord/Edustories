from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
import unicodedata

from .enums import NodeStatuses


def _normalize_answer(s: str) -> str:
    """Приводит ответ к каноническому виду для сравнения."""
    s = unicodedata.normalize("NFKC", s)
    return " ".join(s.strip().lower().split())

@dataclass(frozen=True)
class QuestionRevision:
    """Ревизия конкретного вопроса. Immutable."""

    uid: UUID
    question_id: UUID
    text: str
    correct_answer: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_answer_correct(self, user_answer: str) -> bool:
        """Проверяет ответ пользователя"""
        return _normalize_answer(self.correct_answer) == _normalize_answer(user_answer)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuestionRevision):
            return NotImplemented
        return self.uid == other.uid

    def __hash__(self) -> int:
        return hash(self.uid)

    def __repr__(self) -> str:
        return f"QuestionRevision(uid={self.uid}, question_id={self.question_id})"


@dataclass(frozen=True)
class NodeRevision:
    """
    Ревизия узла. Immutable.
    Однажды созданная ревизия никогда не меняется.
    """

    uid: UUID
    node_id: UUID
    title: str
    questions_order: list[UUID] | None = None
    xp_per_node: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Question:
    """Сущность вопроса внутри узла"""

    uid: UUID = field(default_factory=uuid4)
    node_id: UUID | None = None
    order: int = 1
    current_revision: QuestionRevision | None = None

    def update_content(self, text: str, correct_answer: str) -> QuestionRevision:
        """Создаёт новую ревизию вопроса. Старая остаётся в истории."""
        new_revision = QuestionRevision(
            uid=uuid4(),
            question_id=self.uid,
            text=text,
            correct_answer=correct_answer,
        )
        self.current_revision = new_revision
        return new_revision


@dataclass
class Node:
    """Сущность для узла дорожной карты"""
    order: int
    uid: UUID = field(default_factory=uuid4)
    roadmap_id: UUID = None
    title: str = ""
    current_revision: NodeRevision | None = None
    status: NodeStatuses = NodeStatuses.DRAFT
    available_from: datetime | None = None
    wave: float = 1.0
    questions: list[Question] = field(default_factory=list)
    background_image: str = ""

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

    @property
    def can_user_view(self) -> bool:
        """Отвечает за возможность просмотра точки студентом"""
        return self.is_published

    @property
    def can_user_answer(self) -> bool:
        """Отвечает за возможность ответа на вопросы точки"""
        return self.is_published

    def is_available_at(self, moment_datetime: datetime) -> bool:
        """Отвечает за проверку доступности узла в определённый момент времени"""
        if not self.available_from:
            return False
        return moment_datetime >= self.available_from

    def add_question(self, text: str, correct_answer: str) -> Question:
        """Добавляет новый вопрос в узел"""
        question_uid = uuid4()
        first_revision = QuestionRevision(
            uid=uuid4(),
            question_id=question_uid,
            text=text,
            correct_answer=correct_answer,
        )
        new_question = Question(
            uid=question_uid,
            node_id=self.uid,
            order=len(self.questions) + 1,
            current_revision=first_revision,
        )
        self.questions.append(new_question)
        return new_question


@dataclass
class Roadmap:
    """Сущность для дорожной карты"""

    uid: UUID = field(default_factory=uuid4)
    title: str = ""
    points: list[Node] = field(default_factory=list)

    def add_node(self, title: str) -> Node:
        """Создаёт пустой узел. Вопросы добавляются отдельно."""

        new_node = Node(
            uid=uuid4(),
            roadmap_id=self.uid,
            title=title,
            order=len(self.points) + 1,
        )
        self.points.append(new_node)
        return new_node
