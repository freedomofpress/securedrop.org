from django.apps import AppConfig


class GithubConfig(AppConfig):
    name = 'github'

    def ready(self):
        import github.signals  # noqa: F401
