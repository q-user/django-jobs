from django.forms import model_to_dict
from django.test import TestCase, tag

from aggregator.tests.factories import DataSourceFactory
from articles.models import Article
from articles.tests.factories import ArticleFactory


@tag('model')
class ArticleModelTest(TestCase):
    def test_title_generated_upon_clean(self):
        article = ArticleFactory.build(
            title=None,
            source=DataSourceFactory()
        )
        article.full_clean()
        article.save()
        article.refresh_from_db()
        self.assertIsNotNone(article.title)

    def test_full_validate_fills_language_field(self):
        article = ArticleFactory.build(
            text='Период: Дней: 30<br /><br />Бюджет: 30000 RUB<br /> Пишите в телеграм или на почту'
        )
        a = Article.objects.clean_create(
            **model_to_dict(article)
        )
        self.assertIsNotNone(a.language)
