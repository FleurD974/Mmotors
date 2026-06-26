import dj_database_url
import os

from .settings import *

DEBUG = False
TEMPLATE_DEBUG = False

SECRET_KEY = 'jt@(*tw+w-fm3o*kfobfhrkum!-84-h3b5=_$u(1b(9xazvcpp'

ALLOWED_HOSTS = ['mmotors-project-5dec44416bdd.herokuapp.com']

DATABASES['default'] = dj_database_url.config()
