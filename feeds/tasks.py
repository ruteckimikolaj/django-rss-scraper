from urllib.error import URLError

from celery import task
from celery.exceptions import MaxRetriesExceededError
from django.db import transaction

from feeds.models import Source


class FetchFeedTask(task.Task):
    default_retry_delay = 5 * 60  # retry task every 5 minutes

    def run_task_operations(self, source):
        source.update_or_create_feed()
        source.fetch_status = source.FETCH_DONE
        source.save(update_fields=["fetch_status"])

    def run(self, source_id, *args, **kwargs):
        if source_id:
            source = Source.objects.get(id=source_id)
            source.fetch_status = source.FETCH_PENDING
            source.save(update_fields=["fetch_status"])
            try:
                with transaction.atomic():
                    self.run_task_operations(source)
            except (TypeError, URLError) as exc:
                try:
                    raise self.retry((source_id,), exc=exc)
                except MaxRetriesExceededError:
                    source.fetch_status = source.FETCH_FAILED
                    source.save(update_fields=["fetch_status"])
                    return False
            return True
