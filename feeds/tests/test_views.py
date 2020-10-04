from unittest import mock

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from feeds.models import Feed, FeedEntry, Source
from feeds.tests import BaseTestCase


class ViewsTestCase(APITestCase, BaseTestCase):
    def setUp(self) -> None:
        super(ViewsTestCase, self).setUp()
        self.list_urls = [
            reverse("sources-list"),
            reverse("feeds-list"),
            reverse("feed-entries-list"),
        ]

    def test_available_methods_no_user(self):
        # test list views
        for url in self.list_urls:
            # get request
            response_get = self.client.get(url)
            self.assertEqual(response_get.status_code, 200)
            # options request
            response_options = self.client.options(url)
            self.assertEqual(response_options.status_code, 200)
            # head request
            response_head = self.client.head(url)
            self.assertEqual(response_head.status_code, 200)
        # test api root schema
        response = self.client.head(reverse("openapi-schema"))
        self.assertEqual(response.status_code, 200)

    def test_unavailable_methods_no_user(self):
        for url in self.list_urls:
            response_post = self.client.post(url, {})
            self.assertEqual(response_post.status_code, 401)

            response_delete = self.client.delete(url, {})
            self.assertEqual(response_delete.status_code, 401)

            response_put = self.client.put(url, {})
            self.assertEqual(response_put.status_code, 401)

            response_patch = self.client.patch(url, {})
            self.assertEqual(response_patch.status_code, 401)


class SourceViewsTestCase(APITestCase, BaseTestCase):
    def setUp(self) -> None:
        super(SourceViewsTestCase, self).setUp()
        self.url_list = reverse("sources-list")
        self.post_data = self.create_source_data(fetch_interval=self.first_interval.id, user="")
        self.client.force_login(self.user)

        # preload one source obj
        self.source_data = self.create_source_data(fetch_interval=self.first_interval, url=self.fixture_path)
        self.source = Source.objects.create(**self.source_data)

    @mock.patch("feeds.models.Source.aggregated_data", new_callable=mock.PropertyMock)
    def test_source_view_users(self, mock_aggregated_data):
        # mock methods to accept data from file not from url
        mock_aggregated_data.return_value = self.aggregated_data
        post_data = self.create_source_data(fetch_interval=self.first_interval.id, user="", name="different_name")

        # POST data to create new Source instance for first_user
        response = self.client.post(self.url_list, post_data)
        self.assertEqual(response.status_code, 201)
        source = Source.objects.get(user=self.user)

        # POST data to create new Source instance for second_user
        client_second = self.client
        client_second.force_login(self.user_second)
        post_data_second = self.create_source_data(fetch_interval=self.first_interval.id, user="", name="second_name")
        response_second = client_second.post(self.url_list, post_data_second)
        source_second = Source.objects.get(user=self.user_second)
        self.assertContains(response_second, source_second.name, status_code=201)
        self.assertNotContains(response_second, source.name, status_code=201)

    @mock.patch("feeds.models.Source.aggregated_data", new_callable=mock.PropertyMock)
    def test_source_view_set_functional(self, mock_aggregated_data):

        # mock methods to accept data from file not from url
        mock_aggregated_data.return_value = self.aggregated_data
        post_data = self.create_source_data(fetch_interval=self.first_interval.id, user="", name="different_name")

        # POST data to create new Source instance
        response = self.client.post(self.url_list, post_data)
        self.assertEqual(response.status_code, 201)

        # check filtering new obj.
        source = Source.objects.get(name=post_data["name"])
        response_filtered = self.client.get(self.url_list, {"name__icontains": source.name})
        self.assertContains(response_filtered, source.name)

        response_wrong_filter = self.client.get(self.url_list, {"name__icontains": "wrong"})
        self.assertNotContains(response_wrong_filter, source.name)

        # refetch feed of the source
        response_fetch = self.client.get(reverse("sources-fetch", args=[source.id]))
        self.assertTrue(response_fetch.status_code == 202)
        # status of the feed re-fetching
        response_fetch_status = self.client.get(reverse("sources-fetch-status", args=[source.id]))
        self.assertContains(response_fetch_status, source.fetch_status)
        self.assertContains(response_fetch_status, source.get_fetch_status_display())
        self.assertEqual(
            response_fetch_status.data,
            {
                "status_id": source.fetch_status,
                "status_desc": source.get_fetch_status_display(),
                "last_update": source.updated_at,
            },
        )


class FeedsViewsTestCase(APITestCase, BaseTestCase):
    def setUp(self) -> None:
        super(FeedsViewsTestCase, self).setUp()
        self.client.force_login(self.user)

        self.url_list = reverse("feeds-list")

    @mock.patch("feeds.models.Source.aggregated_data", new_callable=mock.PropertyMock)
    def test_feeds_view_users(self, mock_aggregated_data):
        # mock methods to accept data from file not from url
        mock_aggregated_data.return_value = self.aggregated_data
        post_data = self.create_source_data(fetch_interval=self.first_interval.id, user="")

        # POST data to create new Source instance
        self.client.post(reverse("sources-list"), post_data)

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        feed = Feed.objects.get(source__user=self.user)
        self.assertEqual(self.user, feed.source.user)

        # GET raw data entries
        response_entries = self.client.get(reverse("feeds-entries", args=[feed.id]))
        self.assertEqual(response_entries.data, feed.entries)


class FeedsEntriesViewsTestCase(APITestCase, BaseTestCase):
    def setUp(self) -> None:
        super(FeedsEntriesViewsTestCase, self).setUp()
        self.client.force_login(self.user)
        self.url_list = reverse("feed-entries-list")

    @mock.patch("feeds.models.Source.aggregated_data", new_callable=mock.PropertyMock)
    def test_feed_entries_view_users(self, mock_aggregated_data):
        # mock methods to accept data from file not from url
        mock_aggregated_data.return_value = self.aggregated_data
        post_data = self.create_source_data(fetch_interval=self.first_interval.id, user="")

        # POST data to create new Source instance
        self.client.post(reverse("sources-list"), post_data)

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        feed = Feed.objects.get(source__user=self.user)
        qs_feed_entries = FeedEntry.objects.filter(feed=feed)
        feed_entry = qs_feed_entries.first()
        self.assertTrue(
            response.renderer_context["view"].get_queryset().count()
            == qs_feed_entries.select_related("feed", "feed__source").count()
        )
        # read entry
        response_read = self.client.get(reverse("feed-entries-read", args=[feed_entry.id]))
        feed_entry.refresh_from_db()
        self.assertTrue(feed_entry.read)
        self.assertTrue(feed_entry.read == response_read.data["read"])
        self.assertEqual(response_read.status_code, 202)

        # unread entry
        response_unread = self.client.get(reverse("feed-entries-unread", args=[feed_entry.id]))
        feed_entry.refresh_from_db()
        self.assertFalse(feed_entry.read)
        self.assertTrue(feed_entry.read == response_unread.data["read"])
        self.assertEqual(response_unread.status_code, 202)
