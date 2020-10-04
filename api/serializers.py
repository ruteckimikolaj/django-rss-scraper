from rest_framework import serializers

from feeds.models import Feed, FeedEntry, Source


class SourceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=None)
    id = serializers.HyperlinkedRelatedField(view_name="sources-detail", read_only=True)

    class Meta:
        model = Source
        fields = ["user", "id", "name", "url", "fetch_interval"]
        extra_kwargs = {
            "name": {"help_text": "Name of your feed source"},
            "url": {"help_text": "Valid url to feed source"},
            "fetch_interval": {"help_text": "How often your feed will be updated"},
        }

    def create(self, validated_data):
        """
        main purpose of thi overwritten method is to add request.user to the Source model
        @param validated_data: inherited parameter
        @return: instance
        """
        user = validated_data.get("user")
        request = self.context.get("request")
        if not user and request:
            validated_data.update({"user": request.user})
        instance = Source(**validated_data)
        instance.save()
        return instance


class FeedSetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name="feeds-detail", read_only=True)
    source = serializers.HyperlinkedRelatedField(view_name="sources-detail", read_only=True)

    class Meta:
        model = Feed
        fields = ["id", "source", "title", "link", "summary", "tag_line", "url", "published"]


class RawEntriesSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ["entries"]


class FeedEntriesSetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name="feed-entries-detail", read_only=True)
    feed = serializers.HyperlinkedRelatedField(view_name="feeds-detail", read_only=True)

    class Meta:
        model = FeedEntry
        fields = [
            "id",
            "feed",
            "read",
            "title",
            "link",
            "summary",
            "url",
            "published",
            "modified",
            "author",
            "copyright",
        ]
