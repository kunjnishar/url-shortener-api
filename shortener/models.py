from django.db import models
from django.db.models import F
from django.utils import timezone

from shortener.utils import base62_encode


class ShortURL(models.Model):
    """
    Represents a shortened URL mapping.

    The short_code is deterministically derived from the auto-incrementing
    primary key via Base62 encoding, guaranteeing uniqueness without any
    extra collision-detection logic or random generation.
    """

    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=16, unique=True, db_index=True, blank=True)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

    def save(self, *args, **kwargs):
        """
        Persist the instance, assigning a Base62 short_code derived from
        the primary key on first save.

        Since the primary key is only known after the row exists in the
        database, this performs an initial save to obtain the pk, then
        a lightweight second save that writes only the short_code field.
        """
        is_new = self._state.adding

        super().save(*args, **kwargs)

        if is_new and not self.short_code:
            self.short_code = base62_encode(self.pk)
            super().save(update_fields=["short_code"])

    def register_click(self):
        """
        Atomically increment the click counter and stamp last_accessed,
        avoiding race conditions under concurrent redirect requests by
        using an F() expression instead of a read-modify-write cycle.
        """
        type(self).objects.filter(pk=self.pk).update(
            clicks=F("clicks") + 1,
            last_accessed=timezone.now(),
        )
        self.refresh_from_db(fields=["clicks", "last_accessed"])