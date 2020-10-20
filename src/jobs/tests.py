from django.test import TestCase


class ProjectTestCase(TestCase):
    def test_gunicorn_in_the_environment(self):
        import gunicorn
