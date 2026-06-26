import dj_database_url
import os

from .settings import *

DEBUG = False
TEMPLATE_DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['mmotors-project-5dec44416bdd.herokuapp.com']

DATABASES['default'] = dj_database_url.config()

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)
