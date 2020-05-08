import os

import celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobs.settings')

app = celery.Celery('jobs')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
