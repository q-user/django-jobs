import factory
from django.utils import timezone

from articles.models import Article


class ArticleFactory(factory.DjangoModelFactory):
    text = factory.Faker('text', max_nb_chars=500)
    url = factory.Faker('url')
    title = factory.Faker('sentence', nb_words=7)
    source_datetime = factory.Faker(
        'date_time_this_year',
        tzinfo=timezone.get_current_timezone()
    )
    active = factory.Faker('pybool')
    icon_url = factory.Faker('image_url')
    hash = factory.Faker('sha1')

    class Meta:
        django_get_or_create = ('hash',)
        model = Article
