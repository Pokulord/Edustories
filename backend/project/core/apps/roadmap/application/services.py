from uuid import UUID
from datetime import datetime, timezone

from django.db import transaction
from django.db.models import Sum

from core.apps.users.infrastructure.repositories import DjangoUserRepository

from ..domain.entities import Roadmap
from ..domain.exceptions import QuestionNotFoundError
from ..domain.services import PassingPolicy
from ..infrastructure.repositories import RoadmapRepository, QuestionRepository, UserNodeProgressRepository
from ..models import Node, UserNodeProgress


class RoadmapService:
    """Сервис для работы с дорожной картой"""
    
    def __init__(self, roadmap_repo: RoadmapRepository, user_repo: DjangoUserRepository):
        self.repo = roadmap_repo
        self.user_repo = user_repo

    def get_roadmap(self, roadmap_id: UUID) -> Roadmap:
        """Метод для получения дорожной карты"""
        return self.repo.get_by_id(roadmap_id)


class AnswerService:
    """Сервис проверки ответов и обновления прогресса."""

    def __init__(
        self,
        question_repo: QuestionRepository,
        policy: PassingPolicy | None = None,
    ):
        self.question_repo = question_repo
        self.policy = policy or PassingPolicy()

    @transaction.atomic
    def check_answers(
        self,
        node_id: UUID,
        answers: dict[str, str],
        user_id: UUID,
    ) -> dict:
        """
        Проверяет ответы и обновляет прогресс.

        Узел считается пройденным, только если ВСЕ ответы правильные.
        Возвращает results + summary с total_xp.
        """
        # ─── 1. Проверяем ответы ───
        results, correct, total = self._check_all(answers)

        # ─── 2. Загружаем узел и XP ───
        node = self._get_node(node_id)
        xp_for_node = self._get_xp(node)

        # ─── 3. Обновляем прогресс ───
        progress = self._update_progress(
            user_id=user_id,
            node_id=node_id,
            correct=correct,
            total=total,
            xp=xp_for_node,
        )

        # ─── 4. Общий XP пользователя ───
        total_xp = self._get_total_xp(user_id)

        return {
            "results": results,
            "summary": {
                "total": total,
                "correct": correct,
                "is_passed": progress.is_passed,
                "xp_earned": progress.xp_earned,
                "total_xp": total_xp,
                "attempts_count": progress.attempts_count,
            },
        }

    # ─────────────────────────────────────────────────────
    # Проверка ответов
    # ─────────────────────────────────────────────────────

    def _check_all(
        self,
        answers: dict[str, str],
    ) -> tuple[dict, int, int]:
        """Проверяет все ответы. Возвращает (results, correct, total)."""
        results = {}
        correct = 0
        total = 0

        for qid_str, user_answer in answers.items():
            try:
                qid = UUID(qid_str)
                question = self.question_repo.get_by_id(qid)

                if not question.current_revision:
                    results[qid_str] = {"error": "no_revision"}
                    continue

                is_correct = question.current_revision.is_answer_correct(
                    user_answer
                )
                results[qid_str] = {"is_correct": is_correct}

                total += 1
                if is_correct:
                    correct += 1

            except (ValueError, QuestionNotFoundError):
                results[qid_str] = {"error": "not_found"}

        return results, correct, total

    # ─────────────────────────────────────────────────────
    # Обновление прогресса
    # ─────────────────────────────────────────────────────

    def _update_progress(
        self,
        user_id: UUID,
        node_id: UUID,
        correct: int,
        total: int,
        xp: int,
    ) -> UserNodeProgress:
        """Создаёт или обновляет прогресс. Идемпотентно по is_passed."""
        now = datetime.now(timezone.utc)
        is_passed_now = self.policy.is_passed(correct, total)

        progress, created = UserNodeProgress.objects.get_or_create(
            user_id=user_id,
            node_id=node_id,
            defaults={
                "correct_count": correct,
                "total_count": total,
                "attempts_count": 1,
                "is_passed": is_passed_now,
                "xp_earned": xp if is_passed_now else 0,
                "first_passed_at": now if is_passed_now else None,
            },
        )

        if created:
            return progress

        # ─── Обновляем существующий ───
        progress.apply_result(
            correct=correct,
            total=total,
            xp=xp,
            now=now,
        )
        progress.save(update_fields=[
            "correct_count", "total_count", "attempts_count",
            "is_passed", "xp_earned", "first_passed_at", "updated_at",
        ])

        return progress

    # ─────────────────────────────────────────────────────
    # Вспомогательное
    # ─────────────────────────────────────────────────────

    def _get_node(self, node_id: UUID) -> Node:
        try:
            return Node.objects.select_related(
                "current_revision"
            ).get(id=node_id)
        except Node.DoesNotExist:
            raise NodeNotFoundError(f"Узел {node_id} не найден")

    def _get_xp(self, node: Node) -> int:
        if not node.current_revision:
            return 0
        return node.current_revision.xp

    def _get_total_xp(self, user_id: UUID) -> int:
        """Общий XP пользователя по всем пройденным узлам."""
        result = UserNodeProgress.objects.filter(
            user_id=user_id,
            is_passed=True,
        ).aggregate(total=Sum("xp_earned"))
        return result["total"] or 0


class ProgressService:
    """Сервис прогресса пользователя."""

    def __init__(self, progress_repo: UserNodeProgressRepository):
        self.progress_repo = progress_repo

    def get_progress_map(
        self,
        user_id: UUID,
        roadmap_id: UUID,
    ) -> dict[UUID, UserNodeProgress]:
        """Прогресс по узлам карты: {node_id: progress}."""
        return self.progress_repo.get_by_user_and_roadmap(
            user_id=user_id,
            roadmap_id=roadmap_id,
        )

    def get_total_xp(self, user_id: UUID) -> int:
        """Общий XP пользователя."""
        return self.progress_repo.get_total_xp(user_id)