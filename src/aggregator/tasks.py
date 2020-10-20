from celery import shared_task
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from sentry_sdk import capture_message

from aggregator.models import DataSource
from articles.models import Article


@shared_task
def aggregate_content(datasource_id=None):
    if datasource_id:
        datasource = DataSource.objects.get(id=datasource_id)
    else:
        datasource = DataSource.objects.all().order_by('last_use_time').first()
    try:
        data = datasource.get_data()
    except ConnectionError as e:
        capture_message(e, level='debug')

        task = PeriodicTask.objects.filter(
            kwargs__contains=f'"datasource_id": {datasource.id}').first()
        if task and task.interval.every < 60 and task.interval.period == 'minutes':
            task.interval, created = IntervalSchedule.objects.get_or_create(
                every=task.interval.every + 1,
                period='minutes'
            )
            task.save()
        return

    for d in data:
        Article.objects.clean_create(
            source=datasource,
            active=True,
            **d
        )

    datasource.save()
