from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import JSONField
from django.utils.html import format_html
from django_celery_beat.models import SolarSchedule, ClockedSchedule, CrontabSchedule
from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportMixin

from aggregator.models import DataSource, SourceConfiguration
from aggregator.resources import DataSourceResource
from aggregator.tasks import AggregateContent


def run_now(modeladmin, request, queryset):
    for datasource in queryset.iterator():
        AggregateContent().run(datasource_id=datasource.id)


run_now.short_description = 'Запустить сейчас'


class DataSourceAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'picture', 'plugin',)
    fields = ('id', 'title', 'icon', 'icon_url', 'plugin', 'task', 'configuration')
    list_display_links = ('id', 'title')
    readonly_fields = ('id',)

    resource_class = DataSourceResource

    actions = [run_now]

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget}
    }

    def picture(self, obj):  # noqa: R0201
        return format_html(f'<img width="20" src="{settings.MEDIA_URL}{obj.icon}">')

    picture.allow_tags = True


class SourceConfigurationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'datasource',)
    readonly_fields = ('datasource',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('datasource')
        return qs


admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(SourceConfiguration, SourceConfigurationAdmin)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(Group)
