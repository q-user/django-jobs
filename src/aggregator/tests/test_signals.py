import json

from django.test import TestCase

from aggregator.tests.factories import DataSourceFactory


class DataSourcePostSaveSignalTest(TestCase):
    def test_periodic_task_created_for_created_datasource(self):
        datasource = DataSourceFactory()
        task_kwargs = json.loads(datasource.task.kwargs)
        self.assertEqual(task_kwargs['datasource_id'], datasource.id)
        self.assertTrue(datasource.task)
