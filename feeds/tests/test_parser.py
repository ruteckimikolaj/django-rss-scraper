from urllib.error import URLError

from feeds.parsers import RssAggregator
from feeds.tests import BaseTestCase


class ParsersTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(ParsersTestCase, self).setUp()

    def test_RssAggregator_parse_fail(self):
        with self.assertRaises(URLError):
            RssAggregator.parse("https://localhost:8000")

    def test_RssAggregator_serialize_datetime_fail(self):
        with self.assertRaises(TypeError):
            RssAggregator.serialize_datetime("teststing")
