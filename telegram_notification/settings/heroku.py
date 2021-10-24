"""
Production Settings for Heroku
"""

import environ

# If using in your own project, update the project namespace below
from .local import *

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# False if not in os.environ
DEBUG = env('DEBUG')

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd4ikvchpn8alac',
        'HOST': 'ec2-54-216-17-9.eu-west-1.compute.amazonaws.com',
        'PORT': '5432',
        'USER': 'amkuteyplovifm',
        'PASSWORD': 'd72d574c9a76b3a3c70f564a4be727a49d6715b8a0b1c3f728102ab121e7b2a0'
    }
}
