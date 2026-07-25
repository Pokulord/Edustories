from uuid import UUID
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError
from django.db.utils import IntegrityError

from ..application.abc_repositories import AbstractUserRepository
from ..domain.entities import User
from ..domain.enums import UserStatuses

class DjangoUserRepository(AbstractUserRepository):
    """Имплементация репозитория работы с пользователями через Django ORM"""

    def __init__(self):
        self.model = get_user_model()

    def exists_by_email(self, email: str) -> bool:
        return self.model.objects.filter(email=email).exists()

    def create(self, user_entity: User) -> None:
        """Создаёт нового пользователя"""
        try:
            with transaction.atomic():
                django_user = self.model(
                    id=user_entity.uid,
                    email=user_entity.email,
                    first_name=user_entity.first_name,
                    last_name=user_entity.second_name,
                )
                django_user.set_password(user_entity.password)
                django_user.save()
        except IntegrityError as e:
            # Позже создам тут конкретное исключение (пока что возьму исключение от Django)
            raise DatabaseError(f"Integrity error {e}") from e      
    def get_by_email(self, email: str) -> User|None:
        try:
            django_user = self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None
        else:
            return self._to_entity(django_user)      
    def _to_entity(self, django_user) -> User:
        """Преобразовывает ORM-сущность в доменную"""
        return User(
            first_name=django_user.first_name,
            second_name=django_user.last_name,
            password=django_user.password,
            email=django_user.email,
            status=django_user.role
        )
