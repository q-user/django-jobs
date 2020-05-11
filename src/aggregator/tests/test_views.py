import json

from django.test import TestCase
from django.urls import reverse
from django.utils.module_loading import import_string

from aggregator.plugins import PluginBase
from aggregator.tests.factories import DataSourceFactory
from users.tests.factories import UserFactory


class PluginConfigurationViewTest(TestCase):
    def test_view_returns_json_schema_for_plugin(self):
        url = reverse("aggregator:ajax-configuration")
        plugin = list(PluginBase.get_plugins_list())[0]
        data = {'plugin': plugin}
        Plugin = import_string(plugin)
        response = self.client.post(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        plugin_settings = json.loads(response.content.decode())
        for key in Plugin.configuration.keys():
            self.assertIn(key, plugin_settings)


class DataSourceChangeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(is_superuser=True, is_staff=True)
        cls.datasource = DataSourceFactory()

    def test_datasource_change_view_resolves_200(self):
        self.client.force_login(self.user)
        url = reverse("admin:aggregator_datasource_change", args=(self.datasource.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StatsViewTest(TestCase):
    def test_page_can_be_accessed(self):
        response = self.client.get(reverse('aggregator:stats'))
        self.assertEqual(response.status_code, 200)