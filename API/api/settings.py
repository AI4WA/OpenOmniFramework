"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import boto3

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# CHANGE ME: Change this to a random string, and make it within your environment variables
SECRET_KEY = "django-insecure-yk8_z-l5)!2p2ii*^)i&4z)#j94d#f3by&j1*g*ru=)q7m#jw6"
AUTH_USER_MODEL = "authenticate.User"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
# CHANGE ME: Change this to the domain of your frontend
CSRF_TRUSTED_ORIGINS = ["https://openomni.ai4wa.com"]
# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_yasg",
    "import_export",
    "corsheaders",
    "taggit",
    "authenticate",
    "hardware",
    "llm",
    "orchestrator",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "api.urls"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "api.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "yourdbname"),
        "USER": os.environ.get("DB_USER", "youruser"),
        "PASSWORD": os.environ.get("DB_PASS", "yourpassword"),
        "HOST": os.environ.get(
            "DB_SERVICE", "db"
        ),  # Matches the service name in docker-compose
        "PORT": os.environ.get("DB_PORT", 5432),
    }
}
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Australia/Perth"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
CLIENT_DATA_FOLDER = Path(BASE_DIR).parent / "Client"
TMP_FOLDER = Path(BASE_DIR) / "tmp"
TMP_FOLDER.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Replace with your Next.js app origin if you have a frontend
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),  # 5 minutes for an access token
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # 1 day for a refresh token
    # Add any other simplejwt settings here as needed
}

BOTO3_SESSION = boto3.Session(region_name=os.environ.get("AWS_REGION", "us-west-2"))

# update this

CSV_BUCKET = "wa-data-and-llm-platform"  # update this to your S3 bucket name


LOG_DIR = Path(BASE_DIR) / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


MEDIA_LOCAL = True
CLIENT_MEDIA_ROOT = Path(BASE_DIR).parent / "client" / "Listener" / "data"
CLIENT_MEDIA_URL = "/client/"
AI_MEDIA_ROOT = Path(BASE_DIR).parent / "client" / "Responder" / "data"
AI_MEDIA_URL = "/ai"


JAZZMIN_SETTINGS = {
    "site_logo": "admin/imgs/favicon-32x32.png",
    # Copyright on the footer
    "copyright": "UWA NLP TLP GROUP",
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # external url that opens in a new window (Permissions can be added)
        {
            "name": "Latency|Benchmark",
            "url": "/orchestrator/task/benchmark/?cluster=all",
            "new_window": False,
        },
        {
            "name": "Latency|Details",
            "url": "/orchestrator/task/benchmark_detail/?cluster=all",
            "new_window": False,
        },
        {
            "name": "Accuracy|Benchmark",
            "url": "/hardware/datamultimodalconversation/accuracy_benchmark/?cluster=all",
            "new_window": False,
        },
        {
            "name": "Accuracy|Details",
            "url": "/hardware/datamultimodalconversation/accuracy_detail/?cluster=all",
            "new_window": False,
        },
        {
            "name": "Accuracy|Multi-TurnConversation",
            "url": "/hardware/datamultimodalconversation/accuracy_multi_turn_benchmark/?cluster=all",
            "new_window": False,
        },
    ],
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [
        "hardware",
        "orchestrator",
        "llm",
        "authenticate",
        "group",
    ],
}
