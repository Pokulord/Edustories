import re
from dataclasses import dataclass

from .exceptions import InvalidEmailFormatError, ForbiddenEmailDomainError
from .constants import ALLOWED_DOMAINS

@dataclass(frozen=True)
class Email:
    """Объект для валидации email"""
    value: str

    def __post_init__(self):
        # Нормализация
        normalized = str(self.value.strip()).lower()
        object.__setattr__(self, 'value', normalized)

        if not self._is_valid_format(self.value):
            raise InvalidEmailFormatError(
                metadata={"raw_value": self.value}
            )

        if not self._is_allowed_domain(self.value):
            raise ForbiddenEmailDomainError(
                metadata={
                    "raw_value": self.value,
                    "allowed_domains": ALLOWED_DOMAINS
                }
            )

    @staticmethod
    def _is_valid_format(email: str) -> bool:
        """Функция для проверки формата email
        Я сделал её максимально простой, потому что
        у меня есть личная жизнь
        """
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))
    @classmethod
    def _is_allowed_domain(cls, email: str) -> bool:
        """Проверяет email на разрешённые домены"""
        return email.endswith(ALLOWED_DOMAINS)
