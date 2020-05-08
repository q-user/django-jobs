import datetime
import os

import dropbox
from celery import shared_task
from celery.schedules import crontab
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from dropbox.exceptions import ApiError
from sentry_sdk import capture_message

from articles.models import Article
from articles.resources import ArticleResource
from jobs import celery_app


def dropbox_file(filename):
    if not settings.DROPBOX_TOKEN:
        capture_message("dropbox is not set up", level='error')
        raise Exception("dropbox is not set up")

    dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
    try:
        md = dbx.files_get_metadata(f'/{os.path.basename(filename)}')
        if os.path.getsize(filename) > md.size:
            with open(filename, 'rb') as f:
                dbx.files_upload(
                    f.read(),
                    f'/{os.path.basename(filename)}',
                    mode=dropbox.files.WriteMode.overwrite
                )
    except ApiError as e:
        if 'not_found' in str(e.error):
            with open(filename, 'rb') as f:
                dbx.files_upload(
                    f.read(),
                    f'/{os.path.basename(filename)}',
                    mode=dropbox.files.WriteMode.overwrite
                )
        else:
            raise e


def export_datasets():
    def export_dataset(csv_data, filename):
        location = f'/tmp/{filename}'
        try:
            os.remove(location)
        except:
            pass

        with open(location, 'w') as f:
            f.write(csv_data)

    articles_dataset = ArticleResource().export()
    export_dataset(articles_dataset.csv, 'articles.csv')
    call_command('dumpdata', 'aggregator.DataSource', output='/tmp/datasource.json')


@shared_task
def backup_data():
    export_datasets()
    dropbox_file('/tmp/articles.csv')
    dropbox_file('/tmp/datasources.json')
    dropbox_file('/tmp/backup.sql.gz')


@shared_task
def weekly_report():
    week_period = datetime.timedelta(weeks=1)
    weekly_jobs_count = Article.objects.filter(timestamp__gt=week_period).count()
    message = "Новых вакансий за неделю: {}".format(weekly_jobs_count)
    mail.send_mail(
        message=message,
        from_email="stats@django-jobs.ru",
        subject="Статистика django-jobs.ru за неделю",
        recipient_list=['mihpavlov@gmail.com'],
    )


celery_app.conf.beat_schedule = {
    'backup_data': {
        'task': 'articles.tasks.backup_data',
        'schedule': crontab(minute='0', day_of_week='*', hour='1')
    },
    'weekly_report': {
        'task': 'articles.tasks.weekly_report',
        'schedule': crontab(day_of_week='1', minute='0', hour='0')
    },
}
