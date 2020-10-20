import hashlib
import logging
import re

from bs4 import BeautifulSoup
from django.db import models
from django.template.defaultfilters import linebreaks_filter
from django.utils.text import Truncator
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from aggregator.models import DataSource
from articles.managers import ArticleManager

logger = logging.getLogger(__name__)


class Article(models.Model):
    url = models.URLField()
    text = models.TextField()
    title = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    source_datetime = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    active = models.BooleanField(default=True)
    language = models.CharField(max_length=15, null=True, blank=True)
    icon_url = models.URLField(null=True, blank=True)
    hash = models.CharField(
        max_length=40,
        null=False,
        db_index=True,
        editable=False,
        unique=True
    )
    source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )

    objects = ArticleManager()

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return f'{self.title}'

    def full_clean(self, exclude=None, validate_unique=True):
        if not self.title:
            self.title = self.text.splitlines()[0].split('<br>')[0]
            self.title = Truncator(self.title).words(15, html=True)

        if not self.hash:
            self.hash = hashlib.sha1(self.text.encode('utf-8')).hexdigest()

        super().full_clean(exclude, validate_unique)

        if not self.language:
            try:
                cleantext = BeautifulSoup(self.text, 'html.parser').text
                lang = detect(cleantext)
                if lang not in ['en', 'ru', 'uk', 'es']:
                    lang = 'ru'
                self.language = lang
            except LangDetectException as e:
                logger.info(e, exc_info=True)

    def formated_article(self):
        if re.search(r'<.*?>.*<\/.*?>|<br>|<br/>', self.text, re.MULTILINE):
            soup = BeautifulSoup(self.text, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                link['target'] = '_blank'
                link['rel'] = 'nofollow'
            return str(soup)
        return linebreaks_filter(self.text)
