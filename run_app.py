import threading
import webview

webview.settings['ALLOW_DOWNLOADS'] = True

import os
import sys
from pathlib import Path


# Tell Django which settings file to use
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'notes1_class.settings'
)


def start_django():

    import django

    django.setup()

    from django.core.management import execute_from_command_line

    # Find the project folder
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent

    # Database location
    db_path = base_dir / 'db.sqlite3'

    # If database does not exist, create it
    if not db_path.exists():

        execute_from_command_line([
            'manage.py',
            'migrate'
        ])

    # Start Django server
    execute_from_command_line([
        'manage.py',
        'runserver',
        '--noreload',
        '8000'
    ])


def start_app():

    # Start Django in a background thread
    server_thread = threading.Thread(
        target=start_django,
        daemon=True
    )

    server_thread.start()

    # Create the PyWebView application window
    webview.create_window(
        'PRACS - Staff Management System',
        'http://127.0.0.1:8000/'
    )

    # Start PyWebView
    webview.start()


# Run the application when this file is executed directly
if __name__ == '__main__':
    start_app()