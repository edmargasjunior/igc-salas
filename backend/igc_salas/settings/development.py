"""Configurações de desenvolvimento."""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Banco de dados local para desenvolvimento
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='igc_salas_db'),
        'USER': config('POSTGRES_USER', default='igc_admin'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='igc_salas_secure_pass_2025'),
        'HOST': config('POSTGRES_HOST', default='db'),
        'PORT': config('POSTGRES_PORT', default='5432'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Desabilitar cache em desenvolvimento
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

INTERNAL_IPS = ['127.0.0.1']
