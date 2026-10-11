import logging

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

logger = logging.getLogger("security")


class BasicRoleRequiredMixin(UserPassesTestMixin):
    """Универсальный миксин для проверки роли (от него будем наследоваться)"""

    allowed_roles: tuple = ()
    raise_exception = True

    def test_func(self):
        if not self.allowed_roles:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} должен определить allowed_roles"
            )
        
        user = self.request.user

        has_access = user.has_role(*self.allowed_roles)

        if not has_access:
            logger.warning(
                "Доступ запрещён: user=%s, path=%s, required_roles=%s",
                user.email, self.request.path, self.allowed_roles,
            )
        return has_access