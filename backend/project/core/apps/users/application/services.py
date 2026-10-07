from uuid import UUID

from ..domain.entities import UserProfile
from core.apps.roadmap.infrastructure.repositories import (
    UserShardRepository,
    UserNodeProgressRepository
)

from ..infrastructure.repositories import DjangoUserRepository
from ..domain.exceptions import UserNotFoundError


class ProfileService:
    """Сервис для работы с профилем"""
    
    def __init__(
            self,
            user_repo: DjangoUserRepository,
            progress_repo: UserNodeProgressRepository,
            shard_repo: UserShardRepository
    ):
        self.user_repo = user_repo
        self.progress_repo = progress_repo
        self.shard_repo = shard_repo

    def get_profile(self, user_id: UUID) -> UserProfile:
        """Метод для сбора информации профиля пользователя (я его, короче, во view передаю)"""
        result = self.user_repo.get_with_profile(user_id)
        if result is None:
            raise UserNotFoundError(...)

        user, profile = result

        total_xp = self.progress_repo.get_total_xp(user_id)
        shards_count = len(self.shard_repo.list_by_user(user_id))

        # Расчёт уровня

        level, xp_to_next, progress_percent = self._calculate_level(total_xp)


        return UserProfile(
            uid=user.uid,
            username=user.username,
            level=level,
            xp=total_xp,
            xp_to_next_level=xp_to_next,
            xp_progress_percent=progress_percent,
            shards_count=shards_count,
            avatar_path=profile.avatar_path if profile else None,
        )
    
    def _calculate_level(self, xp: int ) -> tuple[int, int, float]:
        """Функция для расчёта уровня"""
        XP_PER_LEVEL = 1000
        level = xp // XP_PER_LEVEL + 1
        xp_in_level = xp % XP_PER_LEVEL
        xp_to_next_level = XP_PER_LEVEL
        progress = xp_in_level / XP_PER_LEVEL * 100
        return level, xp_in_level, int(progress), xp_to_next_level