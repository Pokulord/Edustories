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


@dataclass 
class LoginUserRequest:
    """DTO для login view"""
    email: str
    ip_address: str|None = None
    user_agent: str|None = None


@dataclass
class LoginUserOutput:
    """DTO для передачи данных в login view"""
    uid: str
    role: str
    
