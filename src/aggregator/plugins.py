import time
from datetime import timedelta, datetime

import anymarkup
import feedparser
import requests
from django.conf import settings
from django.utils.datetime_safe import datetime
from requests.exceptions import SSLError


def words_in_string(words_list, a_string):
    a_string = a_string.lower()
    for word in words_list:
        if word.lower() in a_string:
            return True
    return False


class PluginBase:
    subclasses = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @classmethod
    def get_plugins_choices(cls):
        for subclass in cls.subclasses:
            module_path_str = f'{subclass.__module__}.{subclass.__name__}'
            yield (module_path_str, subclass.verbose_name)

    @classmethod
    def get_plugins_list(cls):
        for subclass in cls.subclasses:
            module_path_str = f'{subclass.__module__}.{subclass.__name__}'
            yield module_path_str


class MoiKrugPlugin(PluginBase):
    request_headers = {
        'Accept': '*/*',
        'User-Agent': 'django-jobs.ru rss reader'
    }
    configuration = {
        'url': 'https://moikrug.ru/vacancies/rss?currency=rur&currency_cd=0&division_ids%5B%5D=2&divisions%5B%5D=backend&page=1&per_page=25&q=django&remote=1&salary_rur=0',
        'pub_date_format': '%a, %d %b %Y %H:%M:%S %z',
    }
    verbose_name = 'Мой Круг'

    def __init__(self, **configuration):
        if not configuration:
            configuration = self.configuration
        self.url = configuration.get('url', None)
        self.pub_date_format = configuration.get('pub_date_format', None)

    def get_data(self, exclude_urls=()):
        response = requests.get(self.url, headers=self.request_headers)
        entries = anymarkup.parse(response.text)
        data_list = []
        for entry in entries['rss']['channel']['item']:
            if entry['link'] in exclude_urls:
                continue
            data_list.append({
                'url': entry['link'],
                'source_datetime': datetime.strptime(
                    entry['pubDate'], self.pub_date_format
                ),
                'text': entry['description'],
                'title': entry['title'],
                'icon_url': entry.get('image', None)
            })
        return data_list


class RemoteJobPlugin(PluginBase):
    request_headers = {
        'Accept': '*/*',
        'User-Agent': 'django-jobs.ru rss reader'
    }
    configuration = {
        'url': 'https://remote-job.ru/feed/vacancies/jango-jobs.xml?accessKey=DMldIdJiR2TiXVsDk6fS',
        'time_format': '%Y-%m-%d %H:%M:%S',
        'user_agent': 'django-jobs.ru rss reader',
        'stop_words': ['bitrix', '#pydigest'],
        'keywords': ['django удаленно', 'django ищем', 'django специалист', 'django вакансия', 'django'],
    }
    verbose_name = 'Remote Job'

    def __init__(self, **configuration):
        if not configuration:
            configuration = self.configuration
        self.url = configuration.get('url', None)
        self.pub_date_format = configuration.get('time_format', None)
        self.keywords = configuration.get('keywords', None)

    def get_data(self, exclude_urls=()):
        response = requests.get(self.url, headers=self.request_headers)
        entries = anymarkup.parse(response.text)
        data_list = []
        for entry in entries['source']['vacancies']['vacancy']:
            if entry['url'] in exclude_urls:
                continue
            if not words_in_string(
                    self.keywords,
                    entry['description']
            ) and not words_in_string(
                self.keywords,
                entry['job-name']
            ):
                continue

            data_list.append({
                'url': entry['url'],
                'source_datetime': datetime.strptime(
                    entry['creation-date'][:19],
                    self.pub_date_format
                ),
                'text': entry['description'],
                'title': entry['job-name'],
            })

        return data_list


class VKPlugin(PluginBase):
    configuration = {
        'token': '',
        'keywords': [''],
        'stop_words': [''],
        'requires_classification': True,
    }
    verbose_name = 'Вконтакте'

    def __init__(self, **configuration):
        if not configuration:
            configuration = self.configuration
        self.icon_url = configuration.get('icon_url', None)
        self.keywords = configuration.get('keywords', None)
        self.stop_words = configuration.get('stop_words', None)

    def get_newsfeed(self, keyword):
        start_date = datetime.now() - timedelta(days=7)
        unix_start_date = time.mktime(start_date.timetuple())
        result = self.client.newsfeed.search(
            q=keyword,
            extended=1,
            count=50,
            start_time=unix_start_date,
            v='5.73'
        )
        return result

    def get_data(self, exclude_urls=()):
        data = []
        for keyword in self.keywords:
            posts = self.get_posts_by_keyword(keyword)
            data.extend(posts)
        dict_values = dict((d['url'], d) for d in data if d['url'] not in exclude_urls).values()
        data_list = list(dict_values)
        return data_list

    def get_posts_by_keyword(self, keyword):
        feed = self.get_newsfeed(keyword)
        data_list = []
        for post in feed['items']:
            url = f'https://vk.com/wall{post["from_id"]}_{post["id"]}'
            pub_date = datetime.fromtimestamp(post.get('date'))
            text = post.get('text')
            if words_in_string(self.stop_words, text):
                continue
            if not text:
                continue
            data_list.append({
                'url': url,
                'source_datetime': pub_date,
                'text': text,
                'icon_url': self.icon_url
            })
        return data_list


class RssPlugin(PluginBase):
    configuration = {
        'url': 'Адрес рсс канала',
        'time_format': '',
        'user_agent': "%s rss reader" % settings.ALLOWED_HOSTS[0],
        'stop_words': ['bitrix', '#pydigest'],
        'keywords': ['django удаленно', 'django разыскивается', 'django специалист', 'django вакансия', 'django'],
        'use_feedparser': True,
    }
    verbose_name = 'RssPlugin'

    def __init__(self, **configuration):
        self.url = configuration.get('url')
        self.time_format = configuration.get('pub_date_format', None)
        self.user_agent = configuration.get('user_agent', 'UA')
        self.stop_words = configuration.get('stop_words', [])
        self.keywords = configuration.get('keywords')
        self.icon_url = configuration.get('icon_url', None)
        self.use_feedparser = configuration.get('use_feedparser', None)

    def get_rss(self):
        if self.use_feedparser:
            return feedparser.parse(self.url)
        try:
            response = requests.get(
                self.url,
                headers={
                    'User-Agent': "%s rss reader" % settings.ALLOWED_HOSTS[0],
                }
            )
        except SSLError:
            response = requests.get(
                self.url,
                headers={
                    'User-Agent': "%s rss reader" % settings.ALLOWED_HOSTS[0],
                },
                verify=False
            )
        return feedparser.parse(response.text)

    def get_data(self):

        rss = self.get_rss()

        data_list = []

        for entry in rss['entries']:
            url = entry.get('link', '')
            text = entry.get('summary', '')
            title = entry.get('title', '')
            pub_date = entry.get('published_parsed') or entry.get('published', None)

            if words_in_string(self.stop_words, text) or \
                    not words_in_string(self.keywords, text) and \
                    not words_in_string(self.keywords, title):
                continue

            try:
                source_datetime = datetime.fromtimestamp(time.mktime(pub_date))
            except TypeError as e:
                source_datetime = datetime.strptime(pub_date, self.time_format).date()

            data_list.append({
                'url': url,
                'source_datetime': source_datetime,
                'text': text,
                'title': title,
                'icon_url': self.icon_url
            })

        return data_list
