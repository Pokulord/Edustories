from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from uuid import uuid4

from .domain.enums import UserRoles, UserStatuses


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя"""

    def create_user(self, email, password=None, **extra_fields):
        """Функция для создания обычного пользователя
        пароль принимаем = None, потому что в будущем планируется OAUTH
        """
        if not email:
            raise ValueError("Email-адрес обязателен")
        
        self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_pasword(password)
        

class RoleModel(models.Model):
    """Модель для ролей пользователей"""
    code = models.CharField(
        max_length=20,
        primary_key=True,
        choices=[(role.name, role.value) for role in UserRoles]
    )  
    class Meta:
        db_table = "roles"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return UserRoles[self.code].value

