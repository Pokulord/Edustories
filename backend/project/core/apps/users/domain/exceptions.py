"""Модуль с базовыми исключениями, которые могут выбрасываться для пользователя"""

from uuid import UUID

from .enums import UserStatuses
from .value_objects import Email

class DomainError(Exception):
    """Базовая доменная ошибка"""
    error_slug: str = "domain_error"
    message: str = "Произошла ошибка на доменном уровне"

    def __init__(self, message: str | None = None, metadata: dict | None = None):
        if message:
            self.message = message
        self.metadata = metadata if metadata else {}
        super().__init__(self.message)

class BaseUserError(DomainError):
    """Базовая доменная ошибка"""
    error_slug: str = "user_error"
    message: str = "Произошла пользовательская ошибка"


class RoleAlreadyAssingError(BaseUserError):
    """Ошибка, которая выбрасывается, если пользователю уже присвоена та или иная роль"""
    error_slug: str = "role_already_assign"

    def __init__(self, user_id: UUID, role: str):
        message = f"Роль {role} уже присвоена пользователю с id {user_id}"
        super().__init__(message, metadata={"role": role, "user_id": user_id})


class CannotCreateUserError(BaseUserError):
    """Ошибка, которая выбрасывается в процессе создания пользователя"""
    error_slug: str = "user_was_not_created"

    def __init__(self, user_id: UUID):
        message = f"Пользователь {user_id} заблокирован"
        super().__init__(message, metadata={"user_id": user_id})

class UserBlockedError(BaseUserError):
    """Ошибка, которая выбрасывается, если пользователь заблокирован"""
    error_slug: str = "user_blocked"

    def __init__(self, user_id: UUID):
        message = f"Пользователь {user_id} заблокирован"
        super().__init__(message, metadata={"user_id": user_id})


class UserIsNotActiveError(BaseUserError):
    """Ошибка, которая выбрасывается, если пользователь неактивен"""
    error_slug: str = "user_is_not_active"

    def __init__(self, user_id: UUID):
        message = f"Пользователь {user_id} неактивен"
        super().__init__(message, metadata={"user_id": user_id})


class UserEmailAlreadyConfirmedError(BaseUserError):
    """Ошибка, которая выбрасывается в случае, если почта уже подтверждена"""
    error_slug: str = "user_email_already_confirmed"

    def __init__(self, user_id: UUID):
        message = f"Почта пользователя {user_id} уже подтверждена"
        super().__init__(message, metadata={"user_id": user_id})


class UserEmailAlreadyInUseError(BaseUserError):
    """Ошибка, которая выбрасывается в случае, если почта уже занята"""
    error_slug = "email_already_in_use"

    def __init__(self, email: Email):
        message = f"Почта {email.value} уже используется"
        super().__init__(message, metadata={"email": email})


class UserCannotBeActivatedError(BaseUserError):
    """Ошибка, которая выбрасывается, если пользователя нельзя активировать"""
    error_slug: str = "user_cannot_be_activated"

    def __init__(self, user_id: UUID, user_status: UserStatuses):
        message = f"Пользователь {user_id} не может быть активирован"
        super().__init__(message, metadata={
            "user_id": str(user_id),
            "user_status": user_status,
            "reason": self._get_reason(user_status)
        })
  
    def _get_reason(self, current_status: UserStatuses) -> str:
        """Вспомогательная функция для получения причины отказа в активации"""
        reasons = {
            UserStatuses.ACTIVE: "Пользователь уже активен",
            UserStatuses.DELETED: "Пользователь удалён",
            UserStatuses.BLOCKED: "Пользователь заблокирован",
        }

        return reasons.get(current_status, "Неявная причина")


class EmailError(DomainError):
    """Базовая ошибка для Email"""
    error_slug: str = "email_error"


class InvalidEmailFormatError(EmailError):
    """Ошибка, которая указывает на неверный формат email"""
    error_slug: str = "invalid_email_format"
    message: str = "Указан некорректный формат email"


class ForbiddenEmailDomainError(EmailError):
    """Ошибка, которая указывает на неразрешённое доменное имя в email"""
    error_slug: str = "forbidden_email_domain"
    message: str = "Регистрация разрешена только для российских доменов (.ru, .рф, .su)"
