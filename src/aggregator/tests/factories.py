import factory

from aggregator.models import DataSource


class DataSourceFactory(factory.DjangoModelFactory):
    configuration = factory.Sequence(lambda n: {f'{n}': f'n'})

    class Meta:
        model = DataSource
