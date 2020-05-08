import datetime
import logging
import os
import pickle
import random
import string
from functools import lru_cache

import nltk
from bs4 import BeautifulSoup
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ValidationError
from django.db import models
from nltk import collections
from nltk.corpus import stopwords
from sentry_sdk import capture_message

logger = logging.getLogger(__name__)


def words_in_string(word_list, a_string):
    a_string = a_string.lower()
    for word in word_list:
        if word.lower() in a_string:
            return True
    return False


def words_in_list_by_set(word_list, a_string):
    return set(word_list).intersection(a_string.split())


class TextAnalyseManagerMixin(object):
    CLASSIFIER_PICKLE_FILE = '/tmp/classifier.pickle'

    def _clean_words(self, word_list):
        stop_words = stopwords.words('russian')
        stop_words.extend(string.punctuation)
        stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на'])
        word_list = [word for word in word_list if word not in stop_words]
        return word_list

    def _clean_text(self, text):
        return text.replace("«", " ").replace("»", " ").replace("/", " ").replace("\\", " ").replace("+", " ")

    def naive_bayes_data(self, datasource):
        documents = []
        qs = self.get_queryset().filter(source=datasource).order_by('id')[:1000]
        for obj in qs.iterator():
            text = BeautifulSoup(obj.article, "html.parser").get_text()
            text = self._clean_text(text).lower()
            tokens = nltk.word_tokenize(text)
            tokens = self._clean_words(tokens)
            documents.append((tokens, obj.active))
        random.shuffle(documents)
        return documents

    def words_active(self, datasource):
        qs = self.get_queryset().filter(
            active=True, source=datasource
        ).values_list('article', flat=True).order_by('id')[:1000]
        all_words = []
        for article in qs.iterator():
            text = BeautifulSoup(article, "html.parser").get_text()
            text = self._clean_text(text).lower()
            tokens = nltk.word_tokenize(text)
            tokens = self._clean_words(tokens)
            all_words.extend(tokens)
        return all_words

    def all_words(self, datasource):
        qs = self.get_queryset().filter(
            source=datasource
        ).values_list('article', flat=True).order_by('id')[:1000]
        all_words = []
        for article in qs.iterator():
            text = BeautifulSoup(article, "html.parser").get_text()
            text = self._clean_text(text).lower()
            tokens = nltk.word_tokenize(text)
            tokens = self._clean_words(tokens)
            all_words.extend(tokens)
        return all_words

    @lru_cache(maxsize=20164)
    def get_all_words_features(self, queryset):
        all_words = self.all_words(queryset)
        words_dist = nltk.FreqDist(all_words)
        word_features = list(words_dist)[:2000]
        return word_features

    def document_features(self, document, queryset):
        document_words = set(document)
        features = {}
        word_features = self.get_all_words_features(queryset)
        for word in word_features:
            features['contains({})'.format(word)] = (word in document_words)
        return features

    @lru_cache(maxsize=256)
    def get_train_set(self, datasource):
        documents = self.naive_bayes_data(datasource)
        featuresets = [(self.document_features(d, datasource), c) for (d, c) in documents]
        train_set, test_set = featuresets[999:], featuresets[:100]
        return train_set, test_set

    def get_or_create_classifier(self, train_set):
        today = datetime.datetime.today().date()
        two_weeks_delta = datetime.timedelta(weeks=2)

        try:
            pickle_date = os.path.getmtime(self.CLASSIFIER_PICKLE_FILE)
            pickle_date = datetime.datetime.fromtimestamp(pickle_date)

            f = open(self.CLASSIFIER_PICKLE_FILE, 'rb')
            if pickle_date.date() < today - two_weeks_delta:
                classifier = nltk.NaiveBayesClassifier.train(train_set)
                f = open(self.CLASSIFIER_PICKLE_FILE, 'wb')
                pickle.dump(classifier, f)
            else:
                classifier = pickle.load(f)
            f.close()
        except FileNotFoundError as e:
            classifier = nltk.NaiveBayesClassifier.train(train_set)
            f = open(self.CLASSIFIER_PICKLE_FILE, 'wb')
            pickle.dump(classifier, f)
            f.close()

        return classifier

    def classify_article(self, article, datasource):
        train_set, test_set = self.get_train_set(datasource)
        classifier = self.get_or_create_classifier(train_set)
        text = BeautifulSoup(article, "html.parser").get_text()
        text = self._clean_text(text).lower()
        tokens = nltk.word_tokenize(text)
        tokens = self._clean_words(tokens)
        article_features = self.document_features(tokens, datasource)
        return classifier.classify(article_features)

    def show_most_informative_features(self, datasource):
        train_set, test_set = self.get_train_set(datasource)
        classifier = self.get_or_create_classifier(train_set)
        classifier.show_most_informative_features()

    def high_information_words(self, labelled_words, score_fn=nltk.BigramAssocMeasures.chi_sq, min_score=5):
        word_fd = nltk.FreqDist()
        label_word_fd = nltk.ConditionalFreqDist()
        for label, words in labelled_words:
            for word in words:
                word_fd[word] += 1
                label_word_fd[label][word] += 1

        n_xx = label_word_fd.N()
        high_info_words = set()

        for label in label_word_fd.conditions():
            n_xi = label_word_fd[label].N()
            word_scores = collections.defaultdict(int)
            for word, n_ii in label_word_fd[label].items():
                n_ix = word_fd[word]
                score = score_fn(n_ii, (n_ix, n_xi), n_xx)
                word_scores[word] = score
            bestwords = [word for word, score in word_scores.items() if score >= min_score]
            high_info_words |= set(bestwords)

        return high_info_words


class ArticleManager(TextAnalyseManagerMixin, models.Manager):
    def clean_create(self, **kwargs):
        obj = self.model(**kwargs)
        try:
            obj.full_clean()
        except ValidationError as e:
            if 'hash' in e.error_dict or 'article' in e.error_dict:
                logger.info(e, exc_info=False)
                return
            capture_message(e, level='exception')

        if self.get_queryset().filter(url=obj.url).exists(): return None
        if self.all().filter(hash=obj.hash).exists(): return None
        obj.save()
        return obj

    def get_similar_to(self, id, exclude_base=True):
        base_article = self.get_queryset().get(id=id)
        qs = self.get_queryset().annotate(
            similarity=TrigramSimilarity('article', base_article.article)
        )
        if exclude_base:
            qs = qs.exclude(id=id)
        return qs.filter(similarity__gt=0.80)
