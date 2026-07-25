from django.urls import path

from .views import LoginView, RegisterView, ProfileView

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="user_profile"),
]
