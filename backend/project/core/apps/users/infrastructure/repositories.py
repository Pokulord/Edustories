from uuid import UUID
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError
from django.db.utils import IntegrityError
from django.db.models import Sum, IntegerField
from django.db.models.functions import Coalesce

from ..application.abc_repositories import AbstractUserRepository
from ..domain.entities import User, Profile
from ..domain.enums import UserStatuses
from ..domain.pagination import Page
from ..domain.dto import UserListItem
from ..application.levels import calculate_level_info

class DjangoUserRepository(AbstractUserRepository):
    """Имплементация репозитория работы с пользователями через Django ORM"""

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100  # защита от DoS через ?page_size=999999

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
        
    def get_all_users(self):
        """Метод для получения всех пользователей"""

        # Тут 'ленивый запрос' - на данном этапе он просто задаёт QuerySet,
        # но обращения к БД не происходит, так как его время
        # наступает только при обращении к конкретным объектам
        # в цикле, при их приведении к списку и т.д

        queryset = self.model.objects.all().select_related("profile").annotate(xp_total=Coalesce(Sum("node_progress__xp_earned"), 0, output_field=IntegerField())).order_by("-date_joined", "-id")
        print(queryset.query)
        return queryset

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
            date_of_join=django_user.date_joined,
            email=django_user.email,
            status=django_user.role
        )
    
    def _to_list_item(self, orm_user) -> UserListItem:
        """Собирает плоскую read model из ORM-пользователя и связанного профиля."""
        profile = getattr(orm_user, "profile", None)

        print(f"XP_TOTAL -> {orm_user.xp_total}")

        return UserListItem(
            id=orm_user.id,
            email=orm_user.email,
            username=orm_user.username,
            first_name=orm_user.first_name,
            second_name=orm_user.last_name,
            role=orm_user.role,
            date_joined=orm_user.date_joined,
            avatar_url=self._avatar_url(profile),
            display_name=self._display_name(orm_user, profile),
            is_active=orm_user.is_active,
            level=calculate_level_info(total_xp=orm_user.xp_total or 0).level,
        )
    
    @staticmethod
    def _avatar_url(profile) -> str | None:
        """URL аватара или None."""
        if profile is None or not profile.avatar:
            return None
        return profile.avatar.url

    @staticmethod
    def _display_name(orm_user, profile) -> str:
        """Приоритет: Profile.display_name → ФИО → username → email."""
        if profile and profile.display_name:
            return profile.display_name

        parts = [orm_user.first_name, orm_user.last_name]
        full = " ".join(p for p in parts if p)
        if full:
            return full

        return orm_user.username or orm_user.email.split("@")[0]