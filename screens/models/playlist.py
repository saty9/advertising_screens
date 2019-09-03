from datetime import datetime
from django.db import models
from django.db.models import Q
from django.urls import reverse

from screens.models import Source


class Playlist(models.Model):
    name = models.TextField()
    description = models.TextField()
    plays_everything = models.BooleanField(default=False)
    interspersed_source = models.ForeignKey(Source, null=True, default=None, on_delete=models.SET_NULL, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_sources(self):
        now = datetime.now()
        if self.plays_everything:
            return Source.objects\
                .exclude(exclude_from_play_all=True)\
                .exclude(pk=self.interspersed_source_id)\
                .filter(Q(valid_from__lte=now) | Q(valid_from__isnull=True))\
                .filter(Q(expires_at__gte=now) | Q(expires_at__isnull=True))
        else:
            return Source.objects\
                .filter(playlistentry__playlist=self)\
                .exclude(pk=self.interspersed_source_id)\
                .filter(Q(valid_from__lte=now) | Q(valid_from__isnull=True))\
                .filter(Q(expires_at__gte=now) | Q(expires_at__isnull=True))\
                .order_by('playlistentry__number')\

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('screens/playlist_view', args=[str(self.id)])
