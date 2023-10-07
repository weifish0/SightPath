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
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# load env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# TODO
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("Django_SECRET_KEY")


'''
detect if you are running on Render by checking 
if the RENDER environment variable is present in the application environment
'''
# SECURITY WARNING: don't run with debug turned on in production!
# if you are in development, add "DEV" variable into your .env file
DEBUG = 'DEV' in os.environ

"""
if 'loaddata' in sys.argv:
    # is database used sqlite3?
    # disable sqlite foreign key checks
    print("Loading data from fixtures - disabling foreign key checks")
    from django.db.backends.signals import connection_created
    def disable_foreign_keys(sender, connection, **kwargs):
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=OFF;')
    connection_created.connect(disable_foreign_keys)
"""


if "DEV" not in os.environ:
    ALLOWED_HOSTS = ["sightpath.tw", "127.0.0.1", "192.168.43.190", "192.168.22.181", "192.168.22.180"]
    CSRF_TRUSTED_ORIGINS = ['https://sightpath.tw']
else:
    if "TEST_NGROK_URL" in os.environ:
        TEST_NGROK_URL = os.getenv("TEST_NGROK_URL")
        TEST_NGROK_HOST = TEST_NGROK_URL[TEST_NGROK_URL.index("//")+2:]
        
        ALLOWED_HOSTS = ["127.0.0.1", "localhost", TEST_NGROK_HOST]
        CSRF_TRUSTED_ORIGINS = [TEST_NGROK_URL]
    else:
        ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    "base.apps.BaseConfig",
    
    # line login設定
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.line",
    
    # api 設定(暫時用不到)
    "rest_framework",
    "corsheaders",
]

AUTHENTICATION_BACKENDS = (
    # 平台內建登入方式(用自訂的帳號與密碼)
    'django.contrib.auth.backends.ModelBackend',
    
    # django allauth登入 (line登入)
    "allauth.account.auth_backends.AuthenticationBackend",
)

# line login docs https://developers.line.biz/en/docs/line-login/integrate-line-login/#login-flow
SOCIALACCOUNT_PROVIDERS = {
    'line': {
        'APP': {
            'client_id': os.getenv('client_id'),
            'secret': os.getenv("secret"),
            'key': '',
        },
        'SCOPE':[
            "profile",
            "openid",
        ],
        # "AUTH_PARAMS": {
        #     "access_type": "online",
        # }
    }
}

# 使用者使用 line login完成後回到主畫面
LOGIN_REDIRECT_URL = "/"

# TODO
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    "whitenoise.middleware.WhiteNoiseMiddleware",
    
    # api middleware
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
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

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
