"""
Production Settings for Heroku
"""

import environ
from socket import gethostname, gethostbyname 

from .local import *

env = environ.Env(
    DEBUG=(bool, False)
)

DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = [ gethostname(), gethostbyname(gethostname()), ] 

if "DATABASE_URL" in env:
    DATABASES['default'] = env.db('DATABASE_URL')
    DATABASES["default"]["ATOMIC_REQUESTS"] = True
