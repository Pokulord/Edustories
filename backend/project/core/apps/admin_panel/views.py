from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


from core.permissions.mixins import BasicRoleRequiredMixin
from core.apps.users.models import CustomUser
from core.apps.users.application.services import UserService
from core.apps.users.infrastructure.repositories import DjangoUserRepository
# Create your views here.


class UsersListAdminMenu(LoginRequiredMixin, BasicRoleRequiredMixin, View):
    """View для просмотра всех пользователей (админ-панель)"""

    allowed_roles = (CustomUser.Role.ADMIN,)

    def get(self, request):
        page = self._parse_int(request.GET.get("page"), default=1)
        page_size = self._parse_int(request.GET.get("page_size"), default=20)

        service = UserService(DjangoUserRepository())
        result = service.get_users_page(page, page_size)
        return render(request, 'admin_users_list.html', {"page_obj": result})
    

    @staticmethod
    def _parse_int(value: str | None, default: int) -> int:
        """Безопасный парсинг GET-параметров — защита от мусора в query string"""
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default


