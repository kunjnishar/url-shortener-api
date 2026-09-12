from django.urls import path

from shortener.views import (
    ShortenURLCreateView,
    URLAnalyticsView,
    URLRedirectView,
)

app_name = "shortener"

urlpatterns = [
    path("api/shorten/", ShortenURLCreateView.as_view(), name="shorten-create"),
    path("r/<str:short_code>/", URLRedirectView.as_view(), name="url-redirect"),
    path(
        "api/analytics/<str:short_code>/",
        URLAnalyticsView.as_view(),
        name="url-analytics",
    ),
]