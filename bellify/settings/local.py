"""
Django settings for bellify project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import environ
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env.read_env(f'{BASE_DIR}/.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'polymorphic',
    'bellify_bot',
    'youtube',
    'twitch',
    'django_cleanup.apps.CleanupConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bellify.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['landing'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bellify.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_ROOT = f'{BASE_DIR}/media/'
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'landing/'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ABSOLUTE_URL = f'http://127.0.0.1:8000'

TOKEN = env.str('TELEGRAM_TOKEN')

ADMIN_ENDPOINT = env.str('ADMIN_ENDPOINT')

TG_WEBHOOK_ENDPOINT = env.str('TG_WEBHOOK_ENDPOINT')

PROVIDER_TOKEN = env.str('PROVIDER_TOKEN')

BOT_NAME = 'BellifyBot' if not DEBUG else 'TestBellifyBot'

BELLIFY_LINK = 'https://t.me/BellifyBot'

# Celery section

CELERY_BROKER_URL = os.environ.get('REDIS_URL', '') + '/1'
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', '') + '/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'check_twitch': {
        'task': 'bellify.tasks.check_twitch',
        'schedule': crontab(minute='0-59/1'),
    },
    'check_youtube': {
        'task': 'bellify.tasks.check_youtube',
        'schedule': crontab(minute='1-58/3'),
    },
    'check_for_deleted_livestreams': {
        'task': 'bellify.tasks.check_for_deleted_livestreams',
        'schedule': crontab(minute='*/30'),
    }
}

# Configuration settings

SPLITTING_CHARACTER = 'ø'

PAGINATION_SIZE = 10

# Twitch

TWITCH_CLIENT_ID = env.str('TWITCH_CLIENT_ID')

TWITCH_CLIENT_SECRET = env.str('TWITCH_CLIENT_SECRET')

TWITCH_TIME_THRESHOLD = timedelta(minutes=30)

# YouTube

ITERATIONS_TO_SKIP = 5

SESSION_CLIENT_COOKIES = {'CONSENT': 'YES+cb'}

YOUTUBE_TIME_THRESHOLD = {
    True: timedelta(minutes=40),
    False: timedelta(minutes=20)
}

# Upgrades section

CURRENCY = 'USD'
PREMIUM_PRICE = 300

CHANNELS_INFO = {
    'youtube': {
        'name': 'YouTube',
        'initial_number': 5,
        'premium_increase': 5,
        'increase_price': 50,
        'icon': '🟥',
        'increase_amount': [5, 10, 15, 20, 30],
        'is_free': True
    },
    'twitch': {
        'name': 'Twitch',
        'initial_number': 0,
        'premium_increase': 5,
        'increase_price': 25,
        'icon': '🟪',
        'increase_amount': [10, 15, 20, 30, 50],
        'is_free': False
    }
}

# Help section

SAMPLE_CHANNELS_IDS = [
    'UCcAd5Np7fO8SeejB1FVKcYw',
    'UCNruPWfg4GUGw3RcwaKtsXQ',
    'UCbBiC9us6srqQytH22wD7Zw',
    'UC9XTzwex6rGLVUGS9cLKFLw',
    'UCBU8GKSd4NY0wCdcalbaltw',
    'UCgPClNr5VSYC3syrDUIlzLw',
    'UC1zZE_kJ8rQHgLTVfobLi_g',
    'UC4PooiX37Pld1T8J5SYT-SQ',
    'UCakgsb0w7QB0VHdnCc-OVEA',
    'UCJFp8uSYCjXOMnkUyb3CQ3Q',
    'UCBa659QWEk1AI4Tg--mrJ2A'
]
