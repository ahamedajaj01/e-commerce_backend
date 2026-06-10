from django.apps import AppConfig

class CmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cms'

    def ready(self):
        import core.signals  # noqa: F401 — registers file-cleanup signals
