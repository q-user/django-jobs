import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

ALLOWED_HOSTS = ['django-jobs.ru', 'www.django-jobs.ru']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT_5432_TCP_PORT', '5432')
    }
}

DROPBOX_TOKEN = os.environ.get('DROPBOX_TOKEN', '')

DEBUG = False

CELERY_BROKER_URL = os.environ.get('REDIS_URL_0', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL_1', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    }
}

sentry_sdk.init(
    dsn="https://27cc7e4bfde942fbb98a879dde429a93@o80847.ingest.sentry.io/176021",
    integrations=[DjangoIntegration(), CeleryIntegration()]
)
