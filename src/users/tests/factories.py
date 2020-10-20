import factory
from factory.django import DjangoModelFactory

from users.models import User


class UserFactory(DjangoModelFactory):
    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = User
