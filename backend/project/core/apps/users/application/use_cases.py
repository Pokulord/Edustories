from ..domain.entities import User
from .abc_repositories import AbstractUserRepository
from ..domain.value_objects import Email
from ..domain.exceptions import UserEmailAlreadyInUseError
from .dto import CreateUserCommand

class CreateUserUseCase:
    """Сценарий для создания нового пользователя"""

    def __init__(self, user_repository: AbstractUserRepository):
        self.repo = user_repository

    def execute(self, command: CreateUserCommand) -> User:
        """Метод, в котором мы через репозиторий(интерфейс) создаём пользователя"""
        email = Email(command.email)

        if self.repo.exists_by_email(email):
            raise UserEmailAlreadyInUseError(email)
        user = User(
            first_name=command.first_name,
            second_name=command.second_name,
            email=email,
        )

        self.repo.save(user)
        return user

