from django.urls import path

from .views import UsersListAdminMenu


app_name = "admin_menu"

urlpatterns = [
    path('', UsersListAdminMenu.as_view(), name="users_list"),
]