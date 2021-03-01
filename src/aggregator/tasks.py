from django.core.cache import cache
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from sentry_sdk import capture_message

from aggregator.models import DataSource
from articles.models import Article
from jobs.celery import app


class AggregateContent(app.Task):
    name = 'aggregator.aggregate_content'

    @staticmethod
    def get_data(datasource):
        data = []
        try:
            data = datasource.get_data()
        except ConnectionError as e:
            capture_message(e, level='debug')

            task = PeriodicTask.objects.filter(
                kwargs__contains=f'"datasource_id": {datasource.id}').first()
            if task and task.interval.every < 60 and task.interval.period == 'minutes':
                task.interval, _ = IntervalSchedule.objects.get_or_create(
                    every=task.interval.every + 1,
                    period='minutes'
                )
                task.save()
        return data

    @staticmethod
    def save_data(data, datasource):
        counter = 0
        for d in data:
            icon_url = d.pop('icon_url', datasource.icon.url)
            Article.objects.clean_create(
                source=datasource,
                active=True,
                icon_url=icon_url,
                **d
            )
            counter += 1
        return counter

    def run(self, datasource_id=None, *args, **kwargs):
        if datasource_id:
            datasource = DataSource.objects.get(id=datasource_id)
        else:
            datasource = DataSource.objects.all().order_by('last_use_time').first()

        data = self.get_data(datasource)
        save_count = self.save_data(data, datasource)
        if save_count:
            cache.delete('stats_view')

        datasource.save()


app.tasks.register(AggregateContent())
