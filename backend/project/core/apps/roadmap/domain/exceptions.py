from uuid import UUID


class DomainError(Exception):
    """Базовая доменная ошибка"""

    error_slug: str = "domain_error"
    message: str = "Произошла ошибка на доменном уровне"

    def __init__(self, message: str | None = None, metadata: dict | None = None):
        if message:
            self.message = message
        self.metadata = metadata if metadata else {}
        super().__init__(self.message)


class BaseRoadmapError(DomainError):
    """Ошибка для дорожной карты"""

    error_slug: str = "roadmap_error"
    message: str = "Произошла ошибка в модуле дорожных карт"


class RoadmapNotFoundError(BaseRoadmapError):
    """Ошибка, которая вызывается в случае, если дорожная карта не найдена"""

    error_slug = "roadmap_not_found"

    def __init__(self, roadmap_id: UUID):
        message = f"Дорожная карта '{roadmap_id}' не найдена"
        super().__init__(
            message,
            metadata={"roadmap_id": roadmap_id},
        )


class RoadmapArchievedError(BaseRoadmapError):
    """Ошибка, которая вызывается в случае, если дорожная карта заархивирована"""

    error_slug = "roadmap_archieved"

    def __init__(self, roadmap_id: UUID):
        message = f"Дорожная карта '{roadmap_id}' архивная"
        super().__init__(
            message,
            metadata={"roadmap_id": roadmap_id},
        )


class RoadmapAccessDeniedError(BaseRoadmapError):
    """Пользователь не имеет прав на редактирование карты"""

    def __init__(self, roadmap_id: UUID, user_id: UUID):
        message = f"Пользователь '{user_id}' не имеет прав на изменение карты '{roadmap_id}'."
        super().__init__(
            message, metadata={"roadmap_id": roadmap_id, "user_id": user_id}
        )

class QuestionNotFoundError(BaseRoadmapError):
    """Ошибка, которая вызывается в случае, если  вопрос не найден"""

    error_slug = "question_not_found"
    
    def __init__(self, question_id: UUID):
        message = f"Карта с id {question_id} не найдена"
        super().__init__(
            message, metadata={"question_id": question_id}
        )