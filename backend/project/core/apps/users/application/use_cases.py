from ..domain.entities import User
from .abc_repositories import AbstractUserRepository
from ..domain.value_objects import Email
from ..domain.exceptions import UserEmailAlreadyInUseError

class CreateUserUseCase:
    """Сценарий для создания нового пользователя"""

    def __init__(self, user_repository: AbstractUserRepository):
        self.repo = user_repository

    def execute(self, first_name: str, second_name: str, raw_email: str) -> User:
        """Метод, в котором мы через репозиторий(интерферйс) создаём пользователя"""
        email = Email(raw_email)

        if self.repo.exists_by_email(email):
            raise UserEmailAlreadyInUseError(email)
        user = User(
            first_name=first_name,
            second_name=second_name,
            email=email,
        )

        self.repo.save(user)
