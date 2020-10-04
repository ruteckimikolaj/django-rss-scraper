from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _

from feeds.parsers import RssAggregator


class TimestampedMixin(models.Model):
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True


class RSSMixin(object):
    @staticmethod
    def get_aggregated_data(url=None, parsed_data=None) -> RssAggregator:
        """
        if url parameter is provided, it fetches xml from url, parse it and map to rss aggregator.

        @param url: valid rss feed url
        @param parsed_data: feedparser.FeedParserDict data
        @return: RssAggregator()
        @raise: ValueError if none of parameters has been provided
        """
        if url and not parsed_data:
            parsed_data = RssAggregator.parse(url)
        elif not parsed_data and not url:
            raise ValueError("You must provide at least one parameter.")
        aggregated_data = RssAggregator(parsed_data)
        return aggregated_data

    class Meta:
        abstract = True


class Source(TimestampedMixin, RSSMixin):
    """
    Source of RSS Feed.

    @save: post_save signal to create django_celery_beat.PeriodicTask
    with interval populated to the model instance.
    """

    FETCH_FAILED = 0
    FETCH_DONE = 1
    FETCH_PENDING = 2
    FETCH_CHOICES = [
        (FETCH_FAILED, _("Failed")),
        (FETCH_DONE, _("Done")),
        (FETCH_PENDING, _("Pending")),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(_("Name"), db_index=True, max_length=255)
    url = models.URLField(_("url to the xml feed"), db_index=True, max_length=255)
    fetch_interval = models.ForeignKey("django_celery_beat.IntervalSchedule", on_delete=models.PROTECT)
    fetch_status = models.SmallIntegerField(_("Fetch status"), choices=FETCH_CHOICES, default=FETCH_DONE)

    class Meta:
        verbose_name = _("Source")
        verbose_name_plural = _("Sources")

    def __str__(self):
        return self.name

    def _create_feed_data(self, aggregated_data):
        result = {
            "source_id": self.id,
            "title": aggregated_data.title,
            "link": aggregated_data.url,
            "summary": aggregated_data.description,
            "tag_line": aggregated_data.tagline,
            "url": aggregated_data.guid or aggregated_data.url,
            "published": aggregated_data.issued_parsed,
            "modified": aggregated_data.modified_parsed,
            "entries": aggregated_data.items,
        }
        return result

    @property
    def aggregated_data(self):
        aggregated_data = self.get_aggregated_data(url=self.url)
        return aggregated_data

    def update_or_create_feed(self):
        feed_data = self._create_feed_data(self.aggregated_data)
        Feed.objects.update_or_create(source_id=self.id, defaults={**feed_data})

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Source, self).save(force_insert, force_update, using, update_fields)
        if update_fields != ["fetch_status"]:
            self.update_or_create_feed()


class Feed(TimestampedMixin, RSSMixin):
    source = models.OneToOneField(Source, on_delete=models.CASCADE)
    title = models.CharField(_("Title"), db_index=True, max_length=255, null=True)
    link = models.URLField(_("Link"), db_index=True, max_length=255, null=True)
    summary = models.TextField(_("Summary"), null=True)
    tag_line = models.TextField(_("Tag line"), null=True)
    url = models.CharField(_("Url"), max_length=512, null=True)
    published = models.DateTimeField(_("Publication date"), null=True)
    modified = models.DateTimeField(_("Modification date"), null=True)
    entries = JSONField(_("Entries"), default=dict)

    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.source.name} feed"

    def check_update_date(self, update_date):
        if (self.published and update_date > self.published) or (self.modified and update_date > self.modified):
            return True
        return False

    def _create_entry_data(self, aggregated_data):
        result = {
            "feed_id": self.id,
            "title": aggregated_data.title,
            "link": aggregated_data.link,
            "summary": aggregated_data.description,
            "url": aggregated_data.guid or aggregated_data.url,
            "published": aggregated_data.issued_parsed,
            "modified": aggregated_data.modified_parsed,
            "author": aggregated_data.author,
            "copyright": aggregated_data.copyright,
        }
        return result

    def update_or_create_entries(self):
        entry_obj_list = []
        data = self.source.aggregated_data
        feed_entries = data.items
        for entry in feed_entries:
            aggregated_data = self.get_aggregated_data(parsed_data=entry)
            entry_data = self._create_entry_data(aggregated_data)
            obj = FeedEntry(**entry_data)
            entry_obj_list.append(obj)
        if entry_obj_list:
            FeedEntry.objects.bulk_create(entry_obj_list)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Feed, self).save(force_insert, force_update, using, update_fields)
        self.update_or_create_entries()


class FeedEntry(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    read = models.BooleanField(_("Has been read"), default=False)
    title = models.CharField(_("Title"), max_length=255, null=True)
    link = models.CharField(_("Link"), max_length=255, null=True)
    summary = models.TextField(_("Summary"), null=True)
    url = models.CharField(_("Url"), max_length=512, null=True)
    published = models.DateTimeField(_("Publication date"), null=True)
    modified = models.DateTimeField(_("Modification date"), null=True)
    author = models.TextField(_("Author"), max_length=255, null=True)
    copyright = models.TextField(_("Copyright"), max_length=255, null=True)

    class Meta:
        verbose_name = _("Feed entry")
        verbose_name_plural = _("Feed entries")

    def __str__(self):
        return f"Entry {self.id} of {self.feed.source.name} source"
