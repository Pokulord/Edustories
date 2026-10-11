from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass(frozen=True, slots=True)
class UserListItem:
    """Плоская read model для строки в списке пользователей."""
    id: uuid.UUID
    email: str
    username: str | None
    first_name: str
    second_name: str
    role: str
    date_joined: datetime
    avatar_url: str | None
    display_name: str

    @property
    def initials(self) -> str:
        if self.first_name and self.second_name:
            return f"{self.first_name[0]}{self.second_name[0]}".upper()
        return (self.username or self.email)[:2].upper()