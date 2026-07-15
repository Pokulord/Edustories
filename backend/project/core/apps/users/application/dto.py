"""Data-transfer objects"""

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CreateUserCommand():
    """DTO для команды создания пользователя"""
    first_name: str
    second_name: str
    email: str
