import logging

from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ValidationError
from django.db import models
from sentry_sdk import capture_message

logger = logging.getLogger(__name__)


class ArticleManager(models.Manager):
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

    def get_similar_to(self, pk, exclude_base=True):
        base_article = self.get_queryset().get(pk=pk)
        qs = self.get_queryset().annotate(
            similarity=TrigramSimilarity('article', base_article.article)
        )
        if exclude_base:
            qs = qs.exclude(pk=pk)
        return qs.filter(similarity__gt=0.80)
