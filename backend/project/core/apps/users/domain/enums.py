from enum import Enum

class UserRoles(str, Enum):
    """
    Перечисление для ролей пользователя
    """
    STUDENT = "Студент"
    INSTRUCTOR = "Педагог"
    ADMIN = "Админ"


class UserStatuses(str, Enum):
    """
    Перечисление для статусов пользователя
    """
    ACTIVE = "Активный"
    PENDING = "В ожидании подтверждения"
    BLOCKED = "Заблокирован"
    DELETED = "Удалён"

