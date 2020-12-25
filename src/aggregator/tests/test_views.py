from django.test import TestCase
from django.urls import reverse

from aggregator.tests.factories import DataSourceFactory
from users.tests.factories import UserFactory


class DataSourceChangeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(is_superuser=True, is_staff=True)
        cls.datasource = DataSourceFactory()

    def test_datasource_change_view_resolves_200(self):
        self.client.force_login(self.user)
        url = reverse("admin:aggregator_datasource_change", args=(self.datasource.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StatsViewTest(TestCase):
    def test_page_can_be_accessed(self):
        response = self.client.get(reverse('aggregator:stats'))
        self.assertEqual(response.status_code, 200)
