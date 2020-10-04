from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class FeedsConfig(AppConfig):
    name = "feeds"

    def ready(self):
        from feeds.models import Source
        from feeds.signals import delete_source, save_source

        post_save.connect(save_source, Source)
        post_delete.connect(delete_source, Source)
