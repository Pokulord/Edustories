from uuid import UUID

from core.apps.users.infrastructure.repositories import DjangoUserRepository

from ..domain.entities import Roadmap
from ..infrastructure.repositories import RoadmapRepository


class RoadmapService:
    """Сервис для работы с дорожной картой"""
    
    def __init__(self, roadmap_repo: RoadmapRepository, user_repo: DjangoUserRepository):
        self.repo = roadmap_repo
        self.user_repo = user_repo

    def get_roadmap(self, roadmap_id: UUID) -> Roadmap:
        """Метод для получения дорожной карты"""
        return self.repo.get_by_id(roadmap_id)
