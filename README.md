![Djago RSS Scraper](https://github.com/ruteckimikolaj/django_rss_scraper/workflows/Djago%20RSS%20Scraper/badge.svg?branch=master&event=push)

# django_rss_scraper
 simple RSS scraper application which saves RSS feeds to a database and lets a user view and manage feeds they’ve added to the system through an API.

## Features

- A user of this API should be able to:
    - Follow and unfollow multiple feeds
    - List all feeds registered by them
    - List feed items belonging to one feed
    - Mark items as read
    - Filter read/unread feed items per feed and globally (e.g. get all unread items from all feeds or one feed in particular). Order the items by the date of the last update
    - Force a feed update
- Feeds (and feed items) should be updated asynchronously in the background. We use Dramatiq for Sendcloud tasks, but you may use whichever solution you’re comfortable with (e.g. asyncio, Celery).
- Implement a back-off mechanism for feed fetching
- If a feed fails to be updated, the system should fall back for a while.
- After a certain amount of failed tries, the system should stop updating the feed automatically.
- Users should be notified and able to retry the feed update if it is stalled after these failed tries.
- Simulate this behaviour in a test case.



## Stack

- Djano
- Django Rest Framework
- Postgresql
- Celery
- Redis

## Getting started

- Clone the repo: `git clone ` + this repository url

Assuming you have docker and docker-compose installed on your computer:

- build and run docker-compose: `docker-compose up -d`


- migrate database in our django project: `docker-compose exec django python ./manage.py migrate`


- create superuser in project: `docker-compose exec django python ./manage.py createsuperuser`


- django-celery-beat service requires migrations to be done.
Type `docker-compose up -d` again after you migrate your database.

## Explore API
- OpenAPI schema: `localhost:8000/api/`
- Log in: `localhost:8000/api/api-auth/login/?next=/api/v1/sources/`
- API: `localhost:8000/api/v1`
- add your rss url here: `localhost:8000/api/v1/sources`