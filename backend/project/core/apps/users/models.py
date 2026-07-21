from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid

from .domain.enums import UserRoles


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя"""

    def create_user(self, email, password=None, **extra_fields):
        """Функция для создания обычного пользователя
        пароль принимаем = None, потому что в будущем планируется OAUTH
        """
        if not email:
            raise ValueError("Email-адрес обязателен")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создаём суперпользователя с email и паролем
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', self.model.Role.ADMIN)

        return self.create_user(email, password, **extra_fields)
        

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
    

class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Администратор")
        INSTRUCTOR = "INSTRUCTOR", _("Наставник")
        STUDENT = "STUDENT", _("Студент")

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_("Юзернейм пользователя. Необязателен для заполнения"),
        null=True,
        blank=True
    )

    email = models.EmailField(_("email address"), unique=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"Пользователь {self.email}"

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")


    
