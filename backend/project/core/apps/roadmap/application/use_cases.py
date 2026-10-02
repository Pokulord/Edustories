from uuid import UUID

from django.db import transaction

from .services import AnswerService, ShardService
from ..domain.entities import UserMapShard


class SubmitAnswerUseCase:
    """Своего рода оркестратор, который совмещает в себе проверку ответов + выдачу осколков"""

    def __init__(
        self,
        answer_service: AnswerService,
        shard_service: ShardService,
    ):
        self.answer_service = answer_service
        self.shard_service = shard_service

    @transaction.atomic
    def execute(
        self,
        node_id: UUID,
        answers: dict[str, str],
        user_id: UUID,
    ) -> dict:
        """
        Проверяет ответы и выдаёт осколок, если узел пройден.

        Либо прогресс и осколок сохраняются вместе, либо ничего.
        """

        # Проверка ответов + прогресс
        result = self.answer_service.check_answers(
            node_id=node_id,
            answers=answers,
            user_id=user_id,
        )

        # Выдача осколка (если узел пройден)
        awarded_shard: UserMapShard | None = None

        if result["summary"]["is_passed"]:
            awarded_shard = self.shard_service.award_shard_if_passed(
                user_id=user_id,
                node_id=node_id,
            )

        result["shard"] = awarded_shard
        return result