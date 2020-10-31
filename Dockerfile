FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
ADD config/requirements.txt /app/requirements.txt
WORKDIR /app/
USER root
RUN \
    apk add --no-cache jpeg-dev postgresql-libs && \
    apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    g++ \
    python3-dev \
    zlib-dev \
    libxml2-dev
RUN pip install -r requirements.txt
RUN adduser --disabled-password --gecos '' user
USER user
RUN mkdir -p /var/tmp/django_cache && \
    chown user /var/tmp/django_cache && \
    chgrp user /var/tmp/django_cache !
