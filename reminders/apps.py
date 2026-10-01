from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reminders'
    verbose_name = 'Smart Medicine Reminders'

    def ready(self):
        """Start the scheduler when the app is ready."""
        import os, sys
        # Avoid running scheduler during commands (migrate, collectstatic, check, etc.)
        if any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic', 'check', 'test']):
            return
        # Avoid starting persistent daemon threads in serverless environments
        if os.environ.get('VERCEL'):
            return
        try:
            from . import scheduler
            scheduler.start()
        except Exception:
            pass
