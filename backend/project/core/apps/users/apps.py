from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'core.apps.users'
    label = 'users'

    def ready(self):
        from . import signals
