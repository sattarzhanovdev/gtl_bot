# gtl_project/settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET", "dev-secret")
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    # "gtl",
    "gtl.apps.GtlConfig"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "gtl.middleware.JWTAuthMiddleware",  # простая JWT‑аутентификация
]

ROOT_URLCONF = "gtl_project.urls"
TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [],
     "APP_DIRS": True,
     "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
     ]}}
]

WSGI_APPLICATION = "gtl_project.wsgi.application"

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

REST_FRAMEWORK = {"UNAUTHENTICATED_USER": None}

# Env
BOT_TOKEN = os.getenv("BOT_TOKEN", "123456:ABC")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "604800"))  # 7 дней
GAME_FREE_SECONDS = 10
CLICK_RATE_LIMIT = 20  # кликов в секунду (хардкап)