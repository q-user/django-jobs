import re
import time
from datetime import timedelta, datetime

import anymarkup
import feedparser
import markdown
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.template.defaultfilters import linebreaks_filter
from django.utils.datetime_safe import datetime
from requests.exceptions import SSLError

USER_AGENT = settings.DEFAULT_USER_AGENT


class PluginBase:
    subclasses = []

    def __init__(self, configuration=None):
        self.configuration = configuration

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

    def normalize_text(self, text):
        if self.configuration.text_format == 'MARKDOWN':
            return markdown.markdown(text)

        if re.search(r'<.*?>.*<\/.*?>|<br>|<br\/>|<br\ \/>', text, re.MULTILINE):
            soup = BeautifulSoup(text, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                link['target'] = '_blank'
                link['rel'] = 'nofollow'
            return str(soup)
        return linebreaks_filter(text)

    @staticmethod
    def words_in_string(words_list, a_string):
        a_string = a_string.lower()
        for word in words_list:
            if word.lower() in a_string:
                return True
        return False


class MoiKrugPlugin(PluginBase):
    request_headers = {
        'Accept': '*/*',
        'User-Agent': USER_AGENT
    }
    url = 'https://moikrug.ru/vacancies/rss?currency=rur&currency_cd=0&division_ids%5B%5D=2&divisions%5B%5D=backend&page=1&per_page=25&q=django&remote=1&salary_rur=0'
    time_format = '%a, %d %b %Y %H:%M:%S %z'

    verbose_name = 'Мой Круг'

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
                    entry['pubDate'], self.time_format
                ),
                'text': entry['description'],
                'title': entry['title'],
                'icon_url': entry.get('image', None)
            })
        return data_list


class RemoteJobPlugin(PluginBase):
    request_headers = {
        'Accept': '*/*',
        'User-Agent': USER_AGENT
    }
    url = 'https://remote-job.ru/feed/vacancies/jango-jobs.xml?accessKey=DMldIdJiR2TiXVsDk6fS'
    time_format = '%Y-%m-%d %H:%M:%S'
    verbose_name = 'Remote Job'

    def get_data(self, exclude_urls=()):
        response = requests.get(self.url, headers=self.request_headers)
        entries = anymarkup.parse(response.text)
        data_list = []
        for entry in entries['source']['vacancies']['vacancy']:
            if entry['url'] in exclude_urls:
                continue
            if not self.words_in_string(
                    self.configuration.keywords,
                    entry['description']
            ) and not self.words_in_string(
                self.configuration.keywords,
                entry['job-name']
            ):
                continue

            data_list.append({
                'url': entry['url'],
                'source_datetime': datetime.strptime(
                    entry['creation-date'][:19],
                    self.time_format
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
        for keyword in self.configuration.keywords:
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
            if self.words_in_string(self.configuration.stop_words, text):
                continue
            if not text:
                continue
            data_list.append({
                'url': url,
                'source_datetime': pub_date,
                'text': text
            })
        return data_list


class RssPlugin(PluginBase):
    verbose_name = 'RssPlugin'

    def get_rss(self):
        try:
            response = requests.get(
                self.configuration.url,
                headers={
                    'User-Agent': USER_AGENT,
                }
            )
        except SSLError:
            response = requests.get(
                self.configuration.url,
                headers={
                    'User-Agent': USER_AGENT,
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

            if self.words_in_string(self.configuration.stop_words, text) or \
                    not self.words_in_string(self.configuration.keywords, text) and \
                    not self.words_in_string(self.configuration.keywords, title):
                continue

            try:
                source_datetime = datetime.fromtimestamp(time.mktime(pub_date))
            except TypeError as e:
                source_datetime = datetime.strptime(pub_date, self.configuration.time_format).date()

            data_list.append({
                'url': url,
                'source_datetime': source_datetime,
                'text': self.normalize_text(text),
                'title': title
            })

        return data_list
