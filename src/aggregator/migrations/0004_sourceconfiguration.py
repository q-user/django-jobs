# Generated by Django 3.1.2 on 2020-12-19 14:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0003_auto_20201020_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('keywords', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), size=None, blank=True, default=list)),
                ('stop_words', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), size=None, blank=True, default=list)),
                ('time_format', models.CharField(blank=True, default='', max_length=48)),
                ('text_format', models.CharField(choices=[('MARKDOWN', 'Markdown'), ('HTML', 'HTML'), ('PLAIN', 'Plain')], default='PLAIN', max_length=10)),
            ],
            options={
                'verbose_name': 'Запись конфигурации',
                'verbose_name_plural': 'Записи конфигураций',
            },
        ),
    ]