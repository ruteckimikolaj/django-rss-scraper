from unittest import mock

from django_celery_beat.models import PeriodicTask

from feeds.models import Feed, Source
from feeds.tests import BaseTestCase


class ModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(ModelTestCase, self).setUp()
        self.source_data = self.create_source_data(fetch_interval=self.first_interval, url=self.fixture_path)

    @mock.patch("feeds.models.Source.update_or_create_feed")
    def test_source_model_creation(self, mocked):
        mocked.return_value = True
        self.source = Source.objects.create(**self.source_data)
        self.assertEqual(Source.objects.count(), 1)

    def test_source_model_chain_creation(self):
        self.source = Source.objects.create(**self.source_data)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Feed.objects.first().feedentry_set.count(), 10)

    @mock.patch("feeds.signals.save_source")
    @mock.patch("feeds.models.Source.update_or_create_feed")
    def test_source_post_save_signal(self, mocked, mocked_signal):
        mocked.return_value = True
        source = Source.objects.create(**self.source_data)
        self.assertEqual(Source.objects.count(), 1)

        # Test result of post_save signal.
        periodic_task = PeriodicTask.objects.get(name="_".join([source.name, str(source.id)]))
        self.assertTrue(str(source.id) in periodic_task.args)
        self.assertTrue(source.fetch_interval == periodic_task.interval)

        # Test result of post_delete signal.
        source.delete()
        periodic_task_qs = PeriodicTask.objects.filter(name="_".join([source.name, str(source.id)]))
        self.assertFalse(periodic_task_qs.exists())
        self.assertFalse(Source.objects.exists())
