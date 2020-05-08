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
