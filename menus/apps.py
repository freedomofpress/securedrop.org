from django.apps import AppConfig


class MenusConfig(AppConfig):
    name = 'menus'

    def ready(self):
        import menus.signals  # noqa: F401
