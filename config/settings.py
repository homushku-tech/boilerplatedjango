import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

IS_PROD = bool(int(os.environ.get("IS_PROD")))

DEBUG = True

WSGI_APPLICATION = "config.wsgi.application"

ALLOWED_HOSTS = ["*"]

LANGUAGE_CODE = "ru-RU"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User model
AUTH_USER_MODEL = "authentication.CustomUser"

include(
    "components/apps.py",
    "components/database.py",
    "components/middleware.py",
    "components/route.py",
    "components/template.py",
    "components/time.py",
    "components/validator.py",
    "components/csrf.py",
    "components/cors.py",
    "components/rest_framework.py",
    "components/swagger.py",
    "components/email.py",
    "components/jwt.py",
)
