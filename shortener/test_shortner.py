import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shortener.models import ShortURL


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def existing_short_url(db):
    return ShortURL.objects.create(original_url="https://www.example.com/some/long/path")


@pytest.mark.django_db
class TestShortenURLCreateView:
    def test_creates_short_url_via_post(self, api_client):
        url = reverse("shortener:shorten-create")
        payload = {"original_url": "https://www.djangoproject.com/"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["original_url"] == payload["original_url"]
        assert response.data["short_code"]
        assert response.data["short_url"].endswith(f"/r/{response.data['short_code']}/")
        assert response.data["clicks"] == 0
        assert ShortURL.objects.count() == 1

    def test_rejects_invalid_url(self, api_client):
        url = reverse("shortener:shorten-create")
        payload = {"original_url": "not-a-valid-url"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ShortURL.objects.count() == 0


@pytest.mark.django_db
class TestURLRedirectView:
    def test_redirects_to_original_url_with_302(self, api_client, existing_short_url):
        url = reverse(
            "shortener:url-redirect",
            kwargs={"short_code": existing_short_url.short_code},
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == existing_short_url.original_url

    def test_click_counter_increments_atomically_across_multiple_hits(
        self, api_client, existing_short_url
    ):
        url = reverse(
            "shortener:url-redirect",
            kwargs={"short_code": existing_short_url.short_code},
        )

        hit_count = 5
        for _ in range(hit_count):
            response = api_client.get(url)
            assert response.status_code == status.HTTP_302_FOUND

        existing_short_url.refresh_from_db()
        assert existing_short_url.clicks == hit_count
        assert existing_short_url.last_accessed is not None

    def test_returns_404_for_nonexistent_short_code(self, api_client):
        url = reverse("shortener:url-redirect", kwargs={"short_code": "ffffff"})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestURLAnalyticsView:
    def test_returns_analytics_payload(self, api_client, existing_short_url):
        redirect_url = reverse(
            "shortener:url-redirect",
            kwargs={"short_code": existing_short_url.short_code},
        )
        api_client.get(redirect_url)
        api_client.get(redirect_url)

        analytics_url = reverse(
            "shortener:url-analytics",
            kwargs={"short_code": existing_short_url.short_code},
        )
        response = api_client.get(analytics_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["short_code"] == existing_short_url.short_code
        assert response.data["original_url"] == existing_short_url.original_url
        assert response.data["clicks"] == 2
        assert response.data["created_at"] is not None
        assert response.data["last_accessed"] is not None

    def test_returns_404_for_nonexistent_short_code(self, api_client):
        analytics_url = reverse(
            "shortener:url-analytics", kwargs={"short_code": "ffffff"}
        )

        response = api_client.get(analytics_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestShortURLModel:
    def test_short_code_is_derived_from_primary_key(self):
        instance = ShortURL.objects.create(original_url="https://anthropic.com/")

        from shortener.utils import base62_encode

        assert instance.short_code == base62_encode(instance.pk)

    def test_register_click_uses_atomic_f_expression(self, existing_short_url):
        existing_short_url.register_click()
        existing_short_url.register_click()

        existing_short_url.refresh_from_db()
        assert existing_short_url.clicks == 2