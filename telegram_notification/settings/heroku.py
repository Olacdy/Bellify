"""
Production Settings for Heroku
"""

import environ
import dj_database_url

from .local import *

env = environ.Env(
    DEBUG=(bool, False)
)

DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES['default'] = dj_database_url.config(default=env('DATABASE_URI'))
