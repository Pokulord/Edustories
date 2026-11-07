from django.core.paginator import Paginator
import logging
from uuid import UUID

from ..domain.entities import UserProfile, User
from core.apps.roadmap.infrastructure.repositories import (
    UserShardRepository,
    UserNodeProgressRepository
)

from ..infrastructure.repositories import DjangoUserRepository
from ..domain.exceptions import UserNotFoundError
from ..domain.pagination import Page
from .levels import calculate_level_info


logger = logging.getLogger(__name__)

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

        shards_count = len(self.shard_repo.list_by_user(user_id))
        level_info = calculate_level_info(self.progress_repo.get_total_xp(user_id))

        # Расчёт уровня

        return UserProfile(
            uid=user.uid,
            username=user.username,
            level=level_info.level,
            xp=level_info.xp_in_level,
            xp_to_next_level=level_info.xp_to_next_level,
            xp_progress_percent=level_info.progress_percent,
            xp_in_next_level=level_info.xp_in_next_level,
            shards_count=shards_count,
            avatar_path=profile.avatar_path if profile else None,
        )


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, user_repo: DjangoUserRepository):
        self._user_repo = user_repo

    def get_users_page(self, page_num: int, page_size: int):
        """Метод сервиса для получения страницы (как объекта) пользователей"""
        logger.info("Запрошен список пользователей page_num=%s page_size = %s", page_num, page_size)
        queryset = self._user_repo.get_all_users()
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_num)
        page.object_list = [self._user_repo._to_list_item(user) for user in page.object_list]
        stats = {
            "total": paginator.count,
            "active": queryset.filter(is_active=True).count()
        }
        return page, stats