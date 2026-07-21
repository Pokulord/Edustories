"""Data-transfer objects"""

from dataclasses import dataclass
import uuid

from ..domain.enums import UserRoles

@dataclass
class RegisterUserRequest:
    """Запрос на регистрацию пользователя"""
    email: str
    password: str
    first_name: str = ''
    last_name: str = ''
    role: UserRoles = UserRoles.STUDENT


@dataclass
class UserRegisterOutput:
    """DTO для передачи из use-case во view"""
    id: uuid
    email: str
    first_name: str
    last_name: str
