from django.contrib import admin
from django.urls import include, path
from shortener.views import home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("admin/", admin.site.urls),
    path("", include("shortener.urls")),
]