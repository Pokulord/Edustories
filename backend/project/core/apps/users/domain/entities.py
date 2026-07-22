from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .value_objects import Email
from .enums import UserRoles, UserStatuses
from .exceptions import UserIsNotActiveError, UserEmailAlreadyConfirmedError, UserCannotBeActivatedError

@dataclass
class User:
    """Доменная сущность пользователя (априори он не подтверждён)"""
    first_name: str
    second_name: str
    email: Email
    uid: UUID = field(default_factory=uuid4)
    password: str | None = None
    is_email_confirmed: bool = False
    _roles: set[UserRoles] = field(default_factory= lambda: {UserRoles.STUDENT})
    status: UserStatuses = UserStatuses.PENDING

    @property
    def initials(self) -> str:
        """Возвращает инициалы пользователя"""
        return f"{self.first_name[0]}{self.second_name[0]}".upper()

    @property
    def name(self) -> str:
        """Свойство, которое по факту функция и уже она возвращает полное имя пользователя"""
        return f"{self.first_name} {self.second_name}"
    # Бизнес-правила
    @property
    def is_instructor(self) -> bool:
        """Функция для проверки, является ли пользователь педагогом"""
        return UserRoles.INSTRUCTOR in self._roles

    @property
    def is_active(self) -> bool:
        """Функция для проверки, активен ли пользователь"""
        return self.status == UserStatuses.ACTIVE

    @property
    def is_pending(self) -> bool:
        """Функция для проверки, является ли пользователь неподтверждённым"""
        return self.status == UserStatuses.PENDING

    @property
    def can_create_course(self) -> bool:
        """Функция, которая проверяет, может ли пользователь создать курс"""
        return self.is_instructor and self.is_active

    # Действия
    def promote_to_instructor(self) -> None:
        """Функция для повышения пользователя до педагога"""
        if not self.is_active:
            raise UserIsNotActiveError(self.uid)
        self._roles.add(UserRoles.INSTRUCTOR)

    def confirm_email(self) -> None:
        """Функция для подтверждения почты"""
        if self.is_email_confirmed:
            raise UserEmailAlreadyConfirmedError(self.user_id)
        if self.status != UserStatuses.PENDING:
            raise UserCannotBeActivatedError(self.uid, self.status)
        self.is_email_confirmed = True
        self.status = UserStatuses.ACTIVE
