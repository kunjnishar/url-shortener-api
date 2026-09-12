from django.contrib import admin

from shortener.models import ShortURL


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("short_code", "original_url", "clicks", "created_at", "last_accessed")
    search_fields = ("short_code", "original_url")
    readonly_fields = ("short_code", "clicks", "created_at", "last_accessed")