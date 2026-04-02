from django.apps import AppConfig


class LoanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.loan'

    def ready(self):
        # Import signal handlers to initialize real-time notifications
        from . import signals  # noqa: F401

