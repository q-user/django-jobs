import datetime
from unittest import mock

from django.test import tag, TestCase

from aggregator.models import DataSource
from aggregator.tasks import AggregateContent
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
        AggregateContent().run()
        self.assertQuerysetEqual(Article.objects.all(), [
            '<Article: Backend python/Django разработчик>'])

        a = Article.objects.latest('id')
        self.assertIsNotNone(a.picture)

    # pylint: disable=no-self-use
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
        AggregateContent().run()

    # pylint: disable=no-self-use
    def test_task_handles_empty_url(self):
        data = [{
            'source_datetime': datetime.datetime(2021, 4, 12, 11, 19, 17,
                                                 tzinfo=datetime.timezone(
                                                     datetime.timedelta(
                                                         seconds=10800))),
            'text': 'Компания «BOW GROUP» ищет хорошего специалиста на вакансию «Python developer / Python разработчик». От 80 000 ₽ до 120 000 ₽. Полный рабочий день. Можно удалённо. Требуемые навыки: #backend, #middle, #Python, #ООП, #Git, #SQL, #PostgreSQL, #Restfulapi, #Django, #Websockets.',
            'title': 'Требуется «Python developer / Python разработчик» (от 80 000 до 120 000 ₽)',
            'url': ''
        }]
        AggregateContent.save_data(
            data,
            DataSource.objects.first()
        )
