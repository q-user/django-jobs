import datetime
import os
from unittest.mock import patch

import factory
import nltk
from django.db.models.signals import post_save
from django.test import TestCase, tag
from faker import Faker

from articles.managers import ArticleManager
from articles.managers import words_in_string
from articles.models import Article
from articles.tests.factories import ArticleFactory


class UtilsTest(TestCase):
    def test_words_in_string_returns_true_if_there_is_words(self):
        result = words_in_string(
            ['привет'],
            'Привет. Это проверочная строка где есть слово django.'
        )
        self.assertTrue(result)


faker = Faker()


@factory.django.mute_signals(post_save)
@tag('manager')
class ArticleManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.articles = ArticleFactory.create_batch(10)

    def test_returns_new_classifier_when_there_is_no_pickle_file(self):
        classifier = Article.objects.get_or_create_classifier(
            [({'contains(➡)': False, 'contains(требуется)': True, }, False)])
        self.assertIsInstance(classifier, nltk.classify.naivebayes.NaiveBayesClassifier)

    def test_returns_new_classifier_when_pickle_is_more_than_2_weeks_old(self):
        filename = ArticleManager.CLASSIFIER_PICKLE_FILE
        file = open(filename, 'wb')
        file.write(b'')
        file.close()

        today = datetime.datetime.today()
        two_weeks_delta = datetime.timedelta(weeks=2, days=1)
        file_date = today - two_weeks_delta
        os.utime(filename, (file_date.timestamp(), file_date.timestamp()))

        Article.objects.get_or_create_classifier([({'contains(➡)': False, 'contains(требуется)': True, }, False)])

        new_file_date = os.path.getmtime(filename)
        new_file_date = datetime.datetime.fromtimestamp(new_file_date)
        self.assertEqual(new_file_date.date(), today.date())

    @patch('nltk.NaiveBayesClassifier.train')
    @patch('pickle.load')
    def test_pickled_classifier_is_used(
            self, mock_pickle_load, mock_train
    ):
        filename = ArticleManager.CLASSIFIER_PICKLE_FILE
        file = open(filename, 'wb')
        file.write(b'')
        file.close()

        Article.objects.get_or_create_classifier([({'contains(➡)': False, 'contains(требуется)': True, }, False)])
        self.assertTrue(mock_pickle_load.called)
        self.assertFalse(mock_train.called)

    def test_clean_create_validates_and_saves_article_object(self):
        data = {
            'url': 'http://itfreelance.by/vacancyDetail.action?id=8040',
            'source_datetime': datetime.date(2017, 6, 23),
            'text': 'Период: Дней: 30<br /><br />Бюджет: 30000 RUB<br /> Пишите в телеграм или на почту',
            'title': 'Title-t',
            'active': True,
        }
        Article.objects.clean_create(**data)
        self.assertTrue(
            Article.objects.get(url=data.get('url'))
        )

    def test_clean_create_handles_duplicate_article_data(self):
        hash = faker.sha1()

        a1 = Article.objects.clean_create(**{
            'url': faker.url(),
            'source_datetime': faker.date_time_this_year(),
            'text': faker.text(max_nb_chars=300),
            'title': faker.sentence(nb_words=5),
            'active': faker.boolean(),
            'hash': hash,
        })
        a2 = Article.objects.clean_create(**{
            'url': faker.url(),
            'source_datetime': faker.date_time_this_year(),
            'text': faker.text(max_nb_chars=300),
            'title': faker.sentence(nb_words=5),
            'active': faker.boolean(),
            'hash': hash,
        })
        self.assertTrue(a1)
        self.assertFalse(a2)
