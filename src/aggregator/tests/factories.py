import factory
from factory.django import DjangoModelFactory

from aggregator.models import DataSource


class DataSourceFactory(DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=10)
    configuration = factory.Sequence(lambda n: {f'{n}': f'n'})

    class Meta:
        model = DataSource
