from django.conf import settings
from rest_framework import serializers

from shortener.models import ShortURL


class ShortURLSerializer(serializers.ModelSerializer):
    """
    Handles creation payloads (original_url only) and read responses
    that expose the derived short_url plus analytics attributes.
    """

    short_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortURL
        fields = [
            "id",
            "original_url",
            "short_code",
            "short_url",
            "clicks",
            "created_at",
            "last_accessed",
        ]
        read_only_fields = [
            "id",
            "short_code",
            "short_url",
            "clicks",
            "created_at",
            "last_accessed",
        ]

    def get_short_url(self, obj: ShortURL) -> str:
        domain = getattr(settings, "SITE_DOMAIN", "").rstrip("/")
        return f"{domain}/r/{obj.short_code}/"


class ShortURLAnalyticsSerializer(serializers.ModelSerializer):
    """
    Read-only analytics payload for a given short code.
    """

    class Meta:
        model = ShortURL
        fields = [
            "short_code",
            "original_url",
            "clicks",
            "created_at",
            "last_accessed",
        ]
        read_only_fields = fields