from celery import shared_task
from celery.schedules import crontab
from django.core.management import call_command

from jobs import celery_app


@shared_task
def clear_thumbnails():
    call_command('thumbnail', 'clear_delete_all')


celery_app.conf.beat_schedule = {
    'clear_thumbnails': {
        'task': 'articles.tasks.clear_thumbnails',
        'schedule': crontab(minute='0', day_of_week='*', hour='6')
    }
}
