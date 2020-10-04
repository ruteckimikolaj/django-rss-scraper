import logging
from time import mktime, struct_time
from urllib.error import URLError

import feedparser
import pytz
from django.utils import timezone
from django.utils.translation import gettext_lazy

logger = logging.getLogger()


class RssAggregator(object):
    """
    aggregates rss feed content for easier use.
    Requires only source_url as a parameter
    @param parsed_data: feedparser.FeedParserDict data
    """

    items = None
    title = None
    language = None
    author = None
    guid = None
    date = None
    date_parsed = None
    description = None
    url = None
    link = None
    modified = None
    modified_parsed = None
    issued = None
    issued_parsed = None
    copyright = None
    tagline = None

    def __init__(self, parsed_data):
        self.parsed_data = parsed_data
        self.set_properties()

    @staticmethod
    def parse(feed_url) -> feedparser.FeedParserDict:
        """
        @param feed_url: valid rss source url.
        @return: FeedParserDict
        @raise: URLError if parsed data is not available
        """
        try:
            parsed_obj = feedparser.parse(feed_url)
        except URLError as e:
            logger.error(gettext_lazy("Cannot fetch rss feed from source", exec=True))
            raise e
        else:
            return parsed_obj

    @staticmethod
    def serialize_datetime(date_time) -> timezone:
        """
        serialize struct_time to timezone
        @param date_time: time.struct_time
        @return: timezone.datetime
        @raise: TypeError on other data types.
        """
        if isinstance(date_time, struct_time):
            return timezone.datetime.fromtimestamp(mktime(date_time)).replace(tzinfo=pytz.UTC)
        else:
            raise TypeError("Can't convert this type to datetime")

    def set_properties(self):
        """
        set properties for object from parsed_data.
        """

        # assign feed entries from the root of the parsed data
        if hasattr(self.parsed_data, "entries"):
            self.items = self.parsed_data.entries

        #  check if it is a feed root or feed element
        if hasattr(self.parsed_data, "feed"):
            source_data = self.parsed_data.feed
        else:
            source_data = self.parsed_data

        # assign available properties not listed in keymap
        self.title = source_data.title
        self.link = source_data.link

        for key in self.parsed_data.keymap.keys():
            if hasattr(self, key) and not getattr(self, key):
                attr_value = source_data.get(key)
                if isinstance(attr_value, struct_time):
                    attr_value = self.serialize_datetime(attr_value)

                setattr(self, key, attr_value)
