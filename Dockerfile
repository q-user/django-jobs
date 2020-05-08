FROM python:3.8
ENV PYTHONUNBUFFERED 1
ADD config/requirements.txt /app/requirements.txt
WORKDIR /app/
RUN pip install -r requirements.txt && \
    python -m nltk.downloader punkt && \
    python -m nltk.downloader stopwords
RUN adduser --disabled-password --gecos '' user
USER user
RUN mkdir -p /var/tmp/django_cache && \
    chown user /var/tmp/django_cache && \
    chgrp user /var/tmp/django_cache

