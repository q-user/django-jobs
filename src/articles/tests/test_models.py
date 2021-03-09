from django.test import tag, TestCase

from aggregator.tests.factories import DataSourceFactory
from articles.tests.factories import ArticleFactory, PictureFactory


@tag('model')
class ArticleModelTest(TestCase):
    def test_title_generated_upon_clean(self):
        picture = PictureFactory()
        article = ArticleFactory.build(
            title=None,
            source=DataSourceFactory(),
            picture=picture
        )
        article.full_clean()
        article.save()
        article.refresh_from_db()
        self.assertIsNotNone(article.title)
