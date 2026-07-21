from django.db import DatabaseError
import logging
from uuid import uuid4

from ..domain.entities import User
from .abc_repositories import AbstractUserRepository
from ..domain.value_objects import Email
from ..domain.exceptions import UserEmailAlreadyInUseError, CannotCreateUserError
from .dto import RegisterUserRequest, UserRegisterOutput

logger = logging.getLogger(__name__)

class CreateUserUseCase:
    """Сценарий для создания нового пользователя"""

    def __init__(self, user_repository: AbstractUserRepository):
        self.repo = user_repository

    def execute(self, request_dto: RegisterUserRequest) -> UserRegisterOutput:
        """Метод, в котором мы через репозиторий(интерфейс) создаём пользователя"""
        email = Email(request_dto.email)
        uid = uuid4()
        user_entity = User(
            uid=uid,
            email=request_dto.email,
            first_name=request_dto.first_name,
            second_name=request_dto.last_name,
            password=request_dto.password,

        )
        if self.repo.exists_by_email(email):
            raise UserEmailAlreadyInUseError(email)

        try:
            self.repo.create(user_entity)
        except DatabaseError as e:
            logger.error(f"Ошибка при создании пользователя %s", e)
            raise CannotCreateUserError(uid) from e
        else:
            logger.info("Пользователь успешно создан %s", uid)
            return UserRegisterOutput(
                id=uid,
                first_name=request_dto.first_name,
                last_name=request_dto.last_name,
                email=request_dto.email
            )
