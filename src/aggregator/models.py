import json
import os
from urllib.parse import urlsplit, urlparse
from urllib.request import urlretrieve

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import validate_image_file_extension
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.module_loading import import_string
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from aggregator.plugins import PluginBase


class SourceConfiguration(models.Model):
    class TextFormat(models.TextChoices):
        MARKDOWN = 'MARKDOWN', 'Markdown'
        HTML = 'HTML', 'HTML'
        PLAIN = 'PLAIN', 'Plain'

    url = models.URLField()
    keywords = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    stop_words = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    time_format = models.CharField(max_length=48, null=False, blank=True, default='')
    text_format = models.CharField(
        max_length=10,
        choices=TextFormat.choices,
        default=TextFormat.PLAIN
    )

    class Meta:
        verbose_name = 'Запись конфигурации'
        verbose_name_plural = 'Записи конфигураций'

    def __str__(self):
        if hasattr(self, 'datasource'):
            return str(self.datasource)
        return urlparse(self.url).netloc


class DataSource(models.Model):
    title = models.CharField(max_length=128, null=False, blank=False)
    icon = models.ImageField(
        verbose_name='Иконка',
        null=True, blank=True,
        upload_to='datasource_icons/',
        validators=[validate_image_file_extension]
    )
    icon_url = models.URLField(verbose_name='Иконка из интернета', null=True, blank=True)
    plugin = models.CharField(max_length=250, choices=PluginBase.get_plugins_choices())

    configuration = models.OneToOneField(
        SourceConfiguration,
        on_delete=models.CASCADE,
        null=True
    )
    last_use_time = models.DateTimeField(auto_now=True)
    task = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('last_use_time',)
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'

    def __str__(self):
        return f'{self.title} - {self.get_plugin_display()}'

    def get_data(self):
        Plugin = import_string(self.plugin)
        data = Plugin(self.configuration).get_data()
        return data

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.icon_url:
            filename = urlsplit(self.icon_url).path.split('/')[-1]
            path = os.path.join(settings.MEDIA_ROOT, self.icon.field.upload_to)
            if not os.path.exists(path):
                os.makedirs(path)
            r, h = urlretrieve(
                self.icon_url,
                os.path.join(path, filename)
            )

            self.icon = os.path.join(self.icon.field.upload_to, filename)
            self.icon_url = ''
        super().save(force_insert, force_update, using, update_fields)


@receiver(post_save, sender=DataSource, dispatch_uid='datasource_create_periodic_task')
def create_periodic_task(sender, instance, created, **kwargs):
    if created:
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=20,
            period=IntervalSchedule.MINUTES
        )
        instance.task = PeriodicTask.objects.create(
            interval=schedule,
            name=instance.title,
            task='aggregator.aggregate_content',
            kwargs=json.dumps({
                'datasource_id': instance.id
            })
        )
        instance.save()
