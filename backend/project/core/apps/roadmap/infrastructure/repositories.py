from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from ..domain.entities import (
    Node,
    NodeRevision,
    Question,
    QuestionRevision,
    Roadmap,
)
from ..domain.enums import NodeStatuses
from ..domain.services import split_lore_into_pages
from ..domain.exceptions import RoadmapNotFoundError
from ..models import (
    Node as NodeM,
)
from ..models import (
    NodeRevision as NodeRevisionM,
)
from ..models import (
    Question as QuestionM,
)
from ..models import (
    QuestionRevision as QuestionRevisionM,
)
from ..models import (
    Roadmap as RoadmapM,
)


class RoadmapRepository:
    def get_by_id(self, roadmap_id: UUID) -> Roadmap:
        """Используется для получения дорожной карты по ID"""
        try:
            orm = (
                RoadmapM.objects
                .prefetch_related(
                    "nodes__current_revision",
                    "nodes__questions",
                    "nodes__questions__current_revision",
                    "nodes__questions__revisions",
                )
                .get(id=roadmap_id)
            )
            return self._build_roadmap(orm)
        except RoadmapM.DoesNotExist as e:
            raise RoadmapNotFoundError(f"Карта с id {roadmap_id} не найдена") from e

    def _build_roadmap(self, orm_obj: RoadmapM) -> Roadmap:
        """Используется для построения сущности дорожной карты"""
        return Roadmap(
            uid=orm_obj.id,
            title=orm_obj.title,
            points=[self._build_node(node) for node in orm_obj.nodes.all()],
        )

    def _build_node(self, orm_obj: NodeM) -> Node:
        """Используется для построения сущности ноды"""
        return Node(
            uid=orm_obj.id,
            roadmap_id=orm_obj.roadmap,
            order=orm_obj.order,
            status=NodeStatuses(orm_obj.status),
            available_from=orm_obj.available_from,
            current_revision=(
                self._build_node_revision(orm_obj.current_revision)
                if orm_obj.current_revision
                else None
            ),
            pages=split_lore_into_pages(orm_obj.lore),
            questions=[self._build_question(q) for q in orm_obj.questions.all()],
        )

    def _build_node_revision(self, orm_obj: NodeRevisionM) -> NodeRevision:
        """Используется для построения сущности ревизии ноды"""
        return NodeRevision(
            uid=orm_obj.id,
            node_id=orm_obj.node_id,
            title=orm_obj.title,
            questions_order=orm_obj.question_order,
            chapter=orm_obj.chapter,
            tag=orm_obj.tag,
            book=orm_obj.book,
            task=orm_obj.task,
            xp=orm_obj.xp,
            narrator_name=orm_obj.narrator_name,
            narrator_role=orm_obj.narrator_role,
        )

    def _build_question(self, orm_obj: QuestionM) -> Question:
        """Используется для построения сущности вопроса"""
        return Question(
            uid=orm_obj.id,
            node_id=orm_obj.node_id,
            order=orm_obj.order,
            current_revision=(
                self._build_question_revision(orm_obj.current_revision)
                if orm_obj.current_revision
                else None
            ),
        )

    def _build_question_revision(self, orm_obj: QuestionRevisionM) -> QuestionRevision:
        """Используется для построения сущности ревизии вопроса"""
        return QuestionRevision(
            uid=orm_obj.id,
            question_id=orm_obj.question,
            text=orm_obj.text,
            correct_answer=orm_obj.correct_answer,
            created_at=orm_obj.created_at,
        )


class QuestionRepository:
    """Репозиторий для работы с вопросами"""

    def get_by_id(self, question_id: UUID) -> Question:
        """Метод для получения вопроса по id"""
        try:
            orm_object = QuestionM.objects.select_related("current_revision").get(
                id=question_id
            )
        except ObjectDoesNotExist as e:
            return None
        else:
            return self._to_domain(orm_object)

    def get_all_questions_by_node(self, node_id: UUID) -> list[Question] | None:
        """Получить все вопросы по ноде"""
        orm_qs = (
            QuestionM.objects.filter(node_id=node_id)
            .select_related("current_revision")
            .order_by("order")
        )

        return [self._to_domain(orm_object) for orm_object in orm_qs]

    def _to_domain(self, orm_obj: QuestionM) -> Question:
        """Маппер для преобразования вопроса в доменный объект"""
        return Question(
            uid=orm_obj.id,
            node_id=orm_obj.node,
            order=orm_obj.order,
            current_revision=(
                self._revision_to_domain(orm_obj.current_revision)
                if orm_obj.current_revision
                else None
            ),
        )

    def _revision_to_domain(self, orm_obj: QuestionRevisionM) -> QuestionRevision:
        """Маппер для преобразования ревизии в доменный объект"""
        return QuestionRevision(
            uid=orm_obj.id,
            question_id=orm_obj.question,
            text=orm_obj.text,
            correct_answer=orm_obj.correct_answer,
            created_at=orm_obj.created_at,
        )
