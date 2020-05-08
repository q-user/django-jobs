import logging

from sorl.thumbnail.log import ThumbnailLogHandler

from .celery import app as celery_app

__all__ = ['celery_app']

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)

logging.getLogger('sorl.thumbnail').addHandler(handler)
