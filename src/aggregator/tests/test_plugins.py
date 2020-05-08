import os
from unittest.mock import patch, Mock

import feedparser
from django.test import TestCase
from django.utils.module_loading import import_string

from aggregator.models import DataSource
from aggregator.plugins import RemoteJobPlugin, MoiKrugPlugin, RssPlugin


class RemoteJobPluginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.plugin = RemoteJobPlugin()

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
        cls.plugin = MoiKrugPlugin()

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
    @classmethod
    def setUpTestData(cls):
        cls.plugin_path = 'aggregator.plugins.RssPlugin'
        Plugin = import_string(cls.plugin_path)
        configuration = Plugin.configuration
        configuration.update({
            'url': 'https://freelansim.ru/rss/tasks'
        })
        cls.plugin = DataSource(
            plugin=cls.plugin_path,
            configuration=Plugin.configuration
        )

    @patch.object(RssPlugin, 'get_rss')
    def test_plugin_returns_posts_data(self, mock_requests_get):
        rss_mock_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'common_rss.xml')
        rss = feedparser.parse(rss_mock_path)
        mock_requests_get.return_value = rss
        data = self.plugin.get_data()
        self.assertTrue(data)
        self.assertIn('url', data[0])
        self.assertIn('source_datetime', data[0])
        self.assertIn('text', data[0])
        self.assertIn('title', data[0])
        self.assertIn('icon_url', data[0])
