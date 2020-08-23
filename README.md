
![CI](https://github.com/q-user/django-jobs/workflows/CI/badge.svg?branch=master)

Initial setup

    docker-compose -f certbot-compose.yml up
    docker-compose down
    

Startup project

    docker-compose up -d
    

For local development and tests you need only database which you can initialize with

    docker-compose up -d db
    
    