from django.test import TestCase, tag

from aggregator.tests.factories import DataSourceFactory
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
