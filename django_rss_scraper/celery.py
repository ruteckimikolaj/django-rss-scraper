from __future__ import absolute_import, unicode_literals

import os

import celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_rss_scraper.settings")

# sentry_sdk.init(
#     dsn=os.environ.get("DSN"), environment=os.environ.get("ENVIRONMENT"), integrations=[CeleryIntegration()]
# )

app = celery.Celery("django_rss_scraper")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
