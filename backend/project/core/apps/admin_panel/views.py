from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from core.permissions.mixins import BasicRoleRequiredMixin
from core.apps.users.models import CustomUser
from core.apps.users.application.services import UserService
from core.apps.users.infrastructure.repositories import DjangoUserRepository
# Create your views here.


class UsersListAdminMenu(LoginRequiredMixin, BasicRoleRequiredMixin, View):
    """View для просмотра всех пользователей (админ-панель)"""

    allowed_roles = (CustomUser.Role.ADMIN,)
    default_page_size = 5
    max_page_size = 100


    def get(self, request):
        page = self._parse_int(request.GET.get("page"), default=1)
        page_size = self._parse_int(
            request.GET.get("page_size"),
            default=self.default_page_size,
            )

        service = UserService(DjangoUserRepository())
        result, stats = service.get_users_page(page, page_size)
        print(result)
        return render(request, 'admin_users_list.html', {"page_obj": result, "stats": stats})
    

    @staticmethod
    def _parse_int(value: str | None, default: int) -> int:
        """Безопасный парсинг GET-параметров — защита от мусора в query string"""
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default


