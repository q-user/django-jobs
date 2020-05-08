from import_export.resources import ModelResource

from aggregator.models import DataSource


class DataSourceResource(ModelResource):
    class Meta:
        model = DataSource
        skip_unchanged = True
