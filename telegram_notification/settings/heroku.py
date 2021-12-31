"""
Production Settings for Heroku
"""

import environ
from socket import gethostname, gethostbyname 
import dj_database_url

from .local import *

env = environ.Env(
    DEBUG=(bool, False)
)

DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = [ gethostname(), gethostbyname(gethostname()), ] 

DATABASES['default'] = dj_database_url.config(default=env('DATABASE_URI'))
