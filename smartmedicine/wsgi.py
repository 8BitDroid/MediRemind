"""
WSGI config for smartmedicine project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartmedicine.settings')

application = get_wsgi_application()

if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
    from pathlib import Path
    import shutil
    tmp_db = Path('/tmp') / 'db.sqlite3'
    src_db = Path(__file__).resolve().parent.parent / 'db.sqlite3'
    if not tmp_db.exists():
        if src_db.exists():
            shutil.copyfile(src_db, tmp_db)
        else:
            from django.core.management import call_command
            try:
                call_command('migrate', interactive=False)
            except Exception:
                pass

app = application
