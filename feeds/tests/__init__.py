from unittest import mock

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule

from django_rss_scraper.celery import app
from feeds.parsers import RssAggregator


class FeedsTestHelper(object):
    def create_source_data(self, **kwargs):
        data = {
            "name": kwargs.get("name", "test_name"),
            "url": kwargs.get("url", "https://google.com"),
            "fetch_interval": kwargs.get("fetch_interval", None),
            "user": kwargs.get("user", None),
        }
        return data


class BaseTestCase(TestCase, FeedsTestHelper):
    @classmethod
    @mock.patch("django.utils.timezone.now")
    def setUpTestData(cls, mock_timezone):
        # set Celery tasks to be synchronous
        app.conf.task_always_eager = True
        cls.fixture_path = "feeds/tests/fixtures/Algemeen.xml"
        # mock timezone.now
        target = timezone.datetime(2010, 1, 1).replace(tzinfo=pytz.UTC)
        mock_timezone.return_value = target
        # mock data from rss feed
        cls.parsed_data = RssAggregator.parse(cls.fixture_path)
        cls.aggregated_data = RssAggregator(cls.parsed_data)

        # other useful props
        cls.user = User.objects.create(username="first", first_name="first", last_name="first", password="password")
        cls.user_second = User.objects.create(
            username="second", first_name="second", last_name="second", password="password"
        )
        cls.first_interval = IntervalSchedule.objects.get(id=1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
