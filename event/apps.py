from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        import event.signals  # noqa: F401
