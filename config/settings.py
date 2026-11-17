import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('HELPDESK_SECRET_KEY') or get_random_secret_key()
DEBUG = False
ROOT_URLCONF = 'config.urls'


def lista_env(nombre, valor=''):
    return [item.strip() for item in os.getenv(nombre, valor).split(',') if item.strip()]


ALLOWED_HOSTS = lista_env('HELPDESK_HOSTS', 'localhost,127.0.0.1')
CORS_ALLOWED_ORIGINS = lista_env(
    'HELPDESK_CORS', 'http://localhost:4200,http://127.0.0.1:4200'
)
# El modo abierto conserva el comportamiento del mock para una práctica local.
MODO_LOCAL_ABIERTO = os.getenv('HELPDESK_LOCAL_ABIERTO') == '1'
if MODO_LOCAL_ABIERTO:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'helpdesk',
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {'timeout': 20},
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_TZ = True
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['helpdesk.authentication.BearerAuthentication'],
    'DEFAULT_THROTTLE_RATES': {'login': '10/min'},
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
