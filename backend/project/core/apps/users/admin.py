from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Profile

# Register your models here.

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    readonly_fields = ("avatar_preview",)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="100" style="border-radius:50%;" />',
                obj.avatar.url
            )
        return "Нет аватара"

    avatar_preview.short_description = "Превью"

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        "email",
        "username",
        "role",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
        "date_joined",
    )

    search_fields = (
        "email",
        "username",
    )

    ordering = ("-date_joined",)

    readonly_fields = ("id", "date_joined", "last_login")

    inlines = (ProfileInline,)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Персональная информация"), {
            "fields": ("username", "role")
        }),
        (_("Права доступа"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Важные даты"), {
            "fields": ("last_login", "date_joined"),
        }),
        (_("UUID"), {
            "fields": ("id",),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role"),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar_preview")
    search_fields = ("user__email",)
    readonly_fields = ("avatar_preview",)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" style="border-radius:50%;" />',
                obj.avatar.url
            )
        return "Нет аватара"

    avatar_preview.short_description = "Аватар"
