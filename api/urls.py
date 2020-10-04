from django.urls import include, path
from django.utils.html import format_html
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from feeds.views import FeedEntryViewSet, FeedViewSet, SourceViewSet


class DjangoRSSScraper(routers.APIRootView):
    def get_view_name(self) -> str:
        return "Django RSS Scraper"

    def get_view_description(self, html=False) -> str:
        description = """
            Simple Rss scraper, which provides basic functionality of adding rss url source,
            name it and get a list of channel entries
        """
        if html:
            return format_html(f"<p>{description}</p>", description)
        else:
            return description


class DocumentedRouter(routers.DefaultRouter):
    APIRootView = DjangoRSSScraper


router_v1 = DocumentedRouter()
router_v1.register(r"feeds", FeedViewSet, basename="feeds")
router_v1.register(r"feed-entries", FeedEntryViewSet, basename="feed-entries")
router_v1.register(r"sources", SourceViewSet, basename="sources")

urlpatterns = [
    path("v1/", include(router_v1.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "",
        get_schema_view(title="Django RSS Scraper", description="API for all things …", version="v1"),
        name="openapi-schema",
    ),
]
