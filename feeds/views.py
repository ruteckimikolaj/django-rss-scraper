from django.urls import reverse
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.permissions import IsOwnerOrReadOnly
from api.serializers import FeedEntriesSetSerializer, FeedSetSerializer, RawEntriesSetSerializer, SourceSerializer

from .models import Feed, FeedEntry, Source
from .tasks import FetchFeedTask


class SourceViewSet(viewsets.ModelViewSet):
    """
    Sources of RSS feed. All actions available for logged in users.
    @ExtraActions:
        - status: check status of feed update
        @status return: {status_id: 1, status_desc: pending, last_update: str(datetime.datetime)}
        - fetch: fetch feed from the source.url
        @fetch: return: message for human :)
    """

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = {
        "name": ["icontains"],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request and self.request.user:
            return qs.filter(user_id=self.request.user.id)
        return qs.none()

    @action(detail=True, methods=["get"], name="fetch", url_name="fetch")
    def fetch(self, request, pk=None):
        obj = self.get_object()
        status_url = reverse("sources-fetch-status", args=[obj.id])
        if obj:
            if obj.fetch_status == obj.FETCH_PENDING:
                return Response(
                    f"Feed update has already been triggered. Try again later. Check status at {status_url}", status=202
                )
            elif obj.fetch_status != obj.FETCH_PENDING:
                task = FetchFeedTask()
                task.apply_async((obj.id,))
        return Response(f"Feed update has been triggered. Check status at {status_url}", status=202)

    @action(detail=True, methods=["get"], name="Re-fetching status", url_name="fetch-status")
    def status(self, request, pk=None):
        obj = self.get_object()
        return Response(
            {
                "status_id": obj.fetch_status,
                "status_desc": obj.get_fetch_status_display(),
                "last_update": obj.updated_at,
            }
        )


class FeedViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Feed.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = FeedSetSerializer
    filterset_fields = {
        "title": ["icontains"],
        "summary": ["icontains"],
    }

    @action(detail=True, methods=["get"], name="Feed entries raw data", url_name="raw-data")
    def entries(self, request, pk=None):
        obj = self.get_object()
        serializer = RawEntriesSetSerializer(data=request.data)
        if serializer.is_valid():
            return Response(obj.entries)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request and self.request.user:
            return qs.filter(source__user_id=self.request.user.id)
        return qs.none()


class FeedEntryViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = FeedEntry.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = FeedEntriesSetSerializer
    filterset_fields = {
        "feed": ["exact"],
        "read": ["exact"],
        "feed__source__name": ["icontains"],
        "title": ["icontains"],
        "summary": ["icontains"],
        "author": ["icontains"],
    }

    @action(detail=True, methods=["get"], name="Has been read", url_name="read")
    def read(self, request, pk=None):
        obj = self.get_object()
        serializer = FeedEntriesSetSerializer(data=request.data)
        if serializer.is_valid():
            if obj.read:
                return Response(f"{obj} HAS ALREADY BEEN FLAGGED. read = {obj.read}")
            obj.read = True
            obj.save()
            return Response(f"YOU FLAGGED {obj} as read. read = {obj.read}")
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], name="has not been read", url_name="unread")
    def unread(self, request, pk=None):
        obj = self.get_object()
        serializer = FeedEntriesSetSerializer(data=request.data)
        if serializer.is_valid():
            if not obj.read:
                return Response(f"{obj} HAS ALREADY BEEN FLAGGED. read = {obj.read}")
            obj.read = False
            obj.save()
            return Response(f"{obj} HAS BEEN RESTORED. read = {obj.read}")
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request and self.request.user:
            return qs.filter(feed__source__user_id=self.request.user.id)
        return qs.none()
