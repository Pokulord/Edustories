from uuid import UUID
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError
from django.db.utils import IntegrityError

from ..application.abc_repositories import AbstractUserRepository
from ..domain.entities import User, Profile
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

    def get_by_id(self, user_id: UUID) -> User | None:
        """Функция для получения пользователя по id"""
        try:
            orm = self.model.objects.select_related("profile").get(id=user_id)
        except self.model.DoesNotExist as e:
            raise self.model.DoesNotExist from e
        return self._to_entity(orm)
 
    def get_with_profile(
    self, user_id: UUID,
    ) -> tuple[User, Profile | None] | None:
        """Получить пользователя с профилем"""
        try:
            orm = (
                self.model.objects
                .select_related("profile")
                .get(id=user_id)
            )
        except self.model.DoesNotExist:
            return None

        user = self._to_entity(orm)
        profile = self._profile_to_entity(orm.profile) if hasattr(orm, "profile") else None
        return user, profile

    def _profile_to_entity(self, orm_profile) -> Profile | None:
        if orm_profile is None:
            return None
        return Profile(
            uid=orm_profile.id,
            user_id=orm_profile.user_id,
            display_name=orm_profile.display_name or None,
            avatar_path=(
                orm_profile.avatar.name if orm_profile.avatar else None
            ),
            bio=orm_profile.bio,
        )

    def _to_entity(self, django_user) -> User:
        """Преобразовывает ORM-сущность в доменную"""
        return User(
            first_name=django_user.first_name,
            second_name=django_user.last_name,
            username=django_user.username,
            password=django_user.password,
            email=django_user.email,
            status=django_user.role
        )