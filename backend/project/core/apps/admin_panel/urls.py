from django.urls import path

from .views import UsersListAdminMenu


app_name = "admin_menu"

urlpatterns = [
    path('get_all_users', UsersListAdminMenu.as_view(), name="users_list"),
]