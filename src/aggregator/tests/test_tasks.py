import datetime
from unittest import mock

from django.test import TestCase, tag

from aggregator.models import DataSource
from aggregator.tasks import aggregate_content
from aggregator.tests.factories import DataSourceFactory
from articles.models import Article
from articles.tests.factories import ArticleFactory


@tag('task')
class AggregateContentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_source = DataSourceFactory(
            plugin='aggregator.plugins.RssPlugin',
        )

    @mock.patch.object(DataSource, 'get_data')
    def test_task_aggregates_and_saves_content(self, get_data_mock):
        data = [
            {
                'url': 'https://hh.ru/vacancy/26546774',
                'source_datetime': datetime.datetime(2018, 7, 13, 10, 59, 54),
                'text': '<p>Вакансия компании: БОЛЬШАЯ ТРОЙКА</p><p>Создана: 13.07.2018</p><p>Регион: Москва</p><p>Предполагаемый уровень месячного дохода: от\xa0120\xa0000\xa0до\xa0180\xa0000\xa0руб.</p>',
                'title': 'Backend python/Django разработчик',
            }
        ]
        get_data_mock.return_value = data
        aggregate_content()
        self.assertQuerysetEqual(Article.objects.all(), ['<Article: Backend python/Django разработчик>'])

    @mock.patch.object(DataSource, 'get_data')
    def test_task_handles_duplicated_url(self, get_data_mock):
        ArticleFactory(url='https://hh.ru/vacancy/26546774')
        data = [
            {
                'url': 'https://hh.ru/vacancy/26546774',
                'source_datetime': datetime.datetime(2018, 7, 13, 10, 59, 54),
                'text': '<p>Вакансия компании: БОЛЬШАЯ ТРОЙКА</p><p>Создана: 13.07.2018</p><p>Регион: Москва</p><p>Предполагаемый уровень месячного дохода: от\xa0120\xa0000\xa0до\xa0180\xa0000\xa0руб.</p>',
                'title': 'Backend python/Django разработчик',
            }
        ]
        get_data_mock.return_value = data
        aggregate_content()
