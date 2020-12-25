import factory
from factory.django import DjangoModelFactory

from aggregator.models import DataSource, SourceConfiguration


class SourceConfigurationFactory(DjangoModelFactory):
    url = factory.Faker('uri')
    keywords = factory.List(['django'])
    text_format = factory.Faker(
        'random_element',
        elements=[x[0] for x in SourceConfiguration.TextFormat.choices]
    )

    class Meta:
        model = SourceConfiguration


class DataSourceFactory(DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=10)
    configuration = factory.SubFactory(SourceConfigurationFactory)

    class Meta:
        model = DataSource
