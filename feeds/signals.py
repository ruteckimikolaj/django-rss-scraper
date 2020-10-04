from django_celery_beat.models import PeriodicTask


def save_source(sender, instance, **kwargs):
    if instance.fetch_status not in [instance.FETCH_PENDING, instance.FETCH_FAILED]:
        PeriodicTask.objects.update_or_create(
            name="_".join([instance.name, str(instance.id)]),
            task="feeds.tasks.FetchFeedTask",
            args=[instance.id],
            defaults={"interval_id": instance.fetch_interval.id},
        )


def delete_source(sender, instance, **kwargs):
    PeriodicTask.objects.filter(
        name="_".join([instance.name, str(instance.id)]),
        task="feeds.tasks.FetchFeedTask",
        args=[instance.id],
    ).delete()
