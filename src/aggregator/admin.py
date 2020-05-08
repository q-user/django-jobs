from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import JSONField
from django.utils.html import format_html
from django_celery_beat.models import SolarSchedule, ClockedSchedule, CrontabSchedule
from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportMixin

from aggregator.models import DataSource
from aggregator.resources import DataSourceResource
from aggregator.tasks import aggregate_content


def run_now(modeladmin, request, queryset):
    for datasource in queryset.iterator():
        aggregate_content(datasource.id)


run_now.short_description = 'Запустить сейчас'


class DataSourceAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'picture', 'plugin',)
    fields = ('id', 'title', 'icon', 'icon_url', 'plugin', 'configuration', 'task')
    list_display_links = ('id', 'title')
    readonly_fields = ('id',)
    # add_form_template = 'admin/datasource_change_form.html'
    # change_form_template = 'admin/datasource_change_form.html'

    resource_class = DataSourceResource

    actions = [run_now]

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget}
    }

    def picture(self, obj):
        return format_html(f'<img width="20" src="{settings.MEDIA_URL}{obj.icon}">')

    picture.allow_tags = True


admin.site.register(DataSource, DataSourceAdmin)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(Group)
