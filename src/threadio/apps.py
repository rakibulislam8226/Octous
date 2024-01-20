from django.apps import AppConfig


class ThreadioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "threadio"

    def ready(self):
        from threadio import signals
