import os
from unittest.mock import patch, Mock

from django.test import TestCase

from aggregator.models import SourceConfiguration
from aggregator.plugins import RemoteJobPlugin, MoiKrugPlugin, RssPlugin
from aggregator.tests.factories import SourceConfigurationFactory


class RemoteJobPluginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.plugin = RemoteJobPlugin(
            configuration=SourceConfigurationFactory()
        )

    @patch('requests.get')
    def test_plugin_returns_posts_data(self, mock_requests_get):
        rss_mock_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'remote-job.xml')
        with open(rss_mock_path, 'r') as xml_file:
            xml = xml_file.read().replace('\n', '')
        mock_requests_get.return_value = Mock(text=xml)

        data = self.plugin.get_data()
        self.assertTrue(data)
        self.assertIn('url', data[0])
        self.assertIn('source_datetime', data[0])
        self.assertIn('text', data[0])
        self.assertIn('title', data[0])


class MoiKrugPluginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.plugin = MoiKrugPlugin(SourceConfigurationFactory())

    @patch('requests.get')
    def test_plugin_return_posts_data(self, mock_requests_get):
        rss_mock_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'moi_krug_rss.xml')
        with open(rss_mock_path, 'r') as xml_file:
            xml = xml_file.read().replace('\n', '')
        mock_requests_get.return_value = Mock(text=xml)

        data = self.plugin.get_data()
        self.assertTrue(data)
        self.assertIn('url', data[0])
        self.assertIn('source_datetime', data[0])
        self.assertIn('text', data[0])
        self.assertIn('title', data[0])
        self.assertIn('icon_url', data[0])


class RssPluginTest(TestCase):
    @patch('requests.get')
    def test_plugin_returns_posts_data(self, mock_requests_get):
        rss_mock_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'common_rss.xml')
        with open(rss_mock_path, 'r') as xml_file:
            xml = xml_file.read().replace('\n', '')
        mock_requests_get.return_value = Mock(text=xml)
        plugin = RssPlugin(SourceConfigurationFactory())
        data = plugin.get_data()
        self.assertTrue(data)
        self.assertIn('url', data[0])
        self.assertIn('source_datetime', data[0])
        self.assertIn('text', data[0])
        self.assertIn('title', data[0])

    @patch('requests.get')
    def test_markdown_is_handled_correctly(self, mock_requests_get):
        rss_mock_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'github.xml')
        with open(rss_mock_path, 'r') as xml_file:
            xml = xml_file.read().replace('\n', '')
        mock_requests_get.return_value = Mock(text=xml)
        configuration = SourceConfigurationFactory(
            text_format=SourceConfiguration.TextFormat.MARKDOWN
        )
        plugin = RssPlugin(configuration)
        data = plugin.get_data()
        self.assertIn('<p>', data[0]['text'])

