from abc import ABC, abstractmethod
from uuid import UUID

from ..domain.entities import User
from ..domain.value_objects import Email

class AbstractUserRepository(ABC):
    """
    Абстрактный класс для репозитория работы с пользователями
    Реализует КРУД (CRUD)
    """
    @abstractmethod
    def get_by_id(self, uid: UUID) -> User | None:
        """Абстрактный метод получения пользователя по id"""
        ...

    @abstractmethod
    def save(self, user: User) -> None:
        """Абстрактный метод создания пользователя"""
        ...

    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        """Абстрактный метод для проверки уникальности email"""
        ...

