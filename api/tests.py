from unittest import mock

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from feeds.models import Source
from feeds.tests import BaseTestCase


class SerializersTestCase(APITestCase, BaseTestCase):
    def setUp(self) -> None:
        super(SerializersTestCase, self).setUp()
        self.url_list = reverse("sources-list")
        self.post_data = self.create_source_data(fetch_interval=self.first_interval.id, user="")
        self.client.force_login(self.user)

    @mock.patch("feeds.models.Source.aggregated_data", new_callable=mock.PropertyMock)
    def test_source_serializer_create(self, mock_aggregated_data):
        # mock methods to accept data from file not from url
        mock_aggregated_data.return_value = self.aggregated_data
        post_data = self.create_source_data(fetch_interval=self.first_interval.id, user="", name="different_name")

        # POST data to create new Source instance for first_user
        response = self.client.post(self.url_list, post_data)
        self.assertEqual(response.status_code, 201)
        source = Source.objects.get(user=self.user)

        self.assertTrue(source.user_id == self.user.id)
