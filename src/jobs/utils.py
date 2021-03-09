import os
import urllib
from urllib.parse import urlsplit
from urllib.request import urlretrieve

from django.conf import settings


def download_image(url, media_path):
    filename = urlsplit(url).path.split('/')[-1]
    path = os.path.join(settings.MEDIA_ROOT, media_path)
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        r, h = urlretrieve(
            url,
            os.path.join(path, filename)
        )
    except urllib.error.HTTPError:
        return ''

    return os.path.join(media_path, filename)
