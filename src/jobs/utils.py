import os
from urllib.parse import urlsplit

import requests
from django.conf import settings


def download_image(url, media_path):
    filename = urlsplit(url).path.split('/')[-1]
    path = os.path.join(settings.MEDIA_ROOT, media_path)
    if not os.path.exists(path):
        os.makedirs(path)

    r = requests.get(url)
    with open(str(os.path.join(path, filename)), 'wb') as f:
        f.write(r.content)

    return os.path.join(media_path, filename)
