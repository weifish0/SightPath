"""
Django settings for sightpath project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import dj_database_url

# load env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# TODO
# SECURITY WARNING: keep the secret key used in production secret!
if 'RENDER' in os.environ:
    print("連接 SECRET_KEY")
    SECRET_KEY = os.environ.get('SECRET_KEY', default='None')
else:
    Django_SECRET_KEY = os.getenv("Django_SECRET_KEY")
    SECRET_KEY = Django_SECRET_KEY


'''
detect if you are running on Render by checking 
if the RENDER environment variable is present in the application environment
'''
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'RENDER' not in os.environ
# DEBUG = True


# TODO
if 'RENDER' in os.environ:
    print("連接 ALLOWED_HOSTS")
    ALLOWED_HOSTS = ["sightpath.tw"]
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:    
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
else:
    ngrok_forwarding = os.getenv("ngrok_forwarding")
    ALLOWED_HOSTS = ["sightpath.tw", "127.0.0.1", ngrok_forwarding]
    CSRF_TRUSTED_ORIGINS = [f'https://{ngrok_forwarding}']



LINE_CHANNEL_ACCESS_TOKEN = os.getenv("line_token")
LINE_CHANNEL_SECRET = os.getenv("line_secret")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    "base.apps.BaseConfig",
    "linebotapp.apps.LinebotappConfig",
    
    "rest_framework",
    
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    "whitenoise.middleware.WhiteNoiseMiddleware",
    
    "corsheaders.middleware.CorsMiddleware",
]

# 建立自己的 user model
AUTH_USER_MODEL = "base.User"

# 暫時先不開放 API 查詢 以減輕伺服器負擔，開啟要先修改允許訪問的名單，用True太危險
# CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "sightpath.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR/"templates"],
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

WSGI_APPLICATION = "sightpath.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if 'RENDER' in os.environ:
    print("連接 DATABASES")
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://postgres:postgres@localhost:8000/',
            conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"

MEDIA_URL = "/images/user_profile_img/"

MEDIA_ROOT = BASE_DIR / "static/images/user_profile_img/"

STATICFILES_DIRS = [
    BASE_DIR / "static"
]


if not DEBUG:    # Tell Django to copy statics to the `staticfiles` directory
    # in your application directory on Render.
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Turn on WhiteNoise storage backend that takes care of compressing static files
    # and creating unique names for each version so they can safely be cached forever.
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
