from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reminders'
    verbose_name = 'Smart Medicine Reminders'

    def ready(self):
        """Start the scheduler when the app is ready."""
        from . import scheduler
        scheduler.start()
