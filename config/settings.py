import os
from pathlib import Path
from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

WSGI_APPLICATION = 'config.wsgi.application'

ALLOWED_HOSTS = []

LANGUAGE_CODE = 'ru-RU'

include(
    'components/apps.py',
    'components/database.py',
    'components/middleware.py',
    'components/route.py',
    'components/template.py',
    'components/time.py',
    'components/validator.py',
    'components/csrf.py',
    'components/cors.py',
    'components/auth.py',
    'components/email.py',
)
