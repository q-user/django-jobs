from django.test import TestCase
from django.urls import reverse

from aggregator.tests.factories import DataSourceFactory
from articles.tests.factories import ArticleFactory


class HomeViewTest(TestCase):
    def test_view_response_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_view_filters_by_language(self):
        ArticleFactory(language="ru", active=True)
        ArticleFactory(language="en", active=True)

        response_ru = self.client.get("/", data={"language": "ru"})
        response_en = self.client.get("/", data={"language": "en"})
        response = self.client.get("/")

        self.assertEqual(response_ru.context_data['object_list'].count(), 1)
        self.assertEqual(response_en.context_data['object_list'].count(), 1)
        self.assertEqual(response.context_data['object_list'].count(), 2)

    def test_filter_by_source(self):
        source = DataSourceFactory()
        ArticleFactory.create_batch(2)
        ArticleFactory.create_batch(
            2, source=source
        )

        url = f"{reverse('aggregator:stats')}?source={source.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_wrong_source_parameter_ignored(self):
        ArticleFactory.create_batch(2)
        url = f"{reverse('aggregator:stats')}?source=x"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
