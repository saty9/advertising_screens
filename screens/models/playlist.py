from datetime import datetime
from django.db import models
from django.db.models import Q
from django.urls import reverse

from screens.models import Source, PlaylistEntry


def flatten(t):
    return [item for sublist in t for item in sublist]


class Playlist(models.Model):
    name = models.TextField()
    description = models.TextField()
    plays_everything = models.BooleanField(default=False)
    interspersed_source = models.ForeignKey(Source, null=True, default=None, on_delete=models.SET_NULL, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    parents = models.ManyToManyField("self", related_name="children", symmetrical=False,
                                     help_text="All sources that would be played by these playlists will be included in this one too.", blank=True)

    def parent_sources(self, block_list):
        block_list.append(self.id)
        return flatten(map(lambda x: x.get_sources(block_list), self.parents.exclude(id__in=block_list)))

    def get_sources(self, block_list = None):
        if block_list is None:
            block_list = []

        now = datetime.now()
        if self.plays_everything:
            valid_sources = Source.objects\
                .exclude(Q(exclude_from_play_all=True) & ~Q(playlistentry__playlist=self))\
                .exclude(pk=self.interspersed_source_id)\
                .filter(Q(valid_from__lte=now) | Q(valid_from__isnull=True))\
                .filter(Q(expires_at__gte=now) | Q(expires_at__isnull=True))
            return [PlaylistEntry(source=s) for s in valid_sources] + self.parent_sources(block_list)
        else:
            return list(self.playlistentry_set.select_related("source") \
                        .exclude(source_id=self.interspersed_source_id) \
                        .filter(Q(source__valid_from__lte=now) | Q(source__valid_from__isnull=True)) \
                        .filter(Q(source__expires_at__gte=now) | Q(source__expires_at__isnull=True)) \
                        .order_by('number')) + self.parent_sources(block_list)
            #return Source.objects\
            #    .filter(playlistentry__playlist=self)\
            #    .exclude(pk=self.interspersed_source_id)\
            #    .filter(Q(valid_from__lte=now) | Q(valid_from__isnull=True))\
            #    .filter(Q(expires_at__gte=now) | Q(expires_at__isnull=True))\
            #    .order_by('playlistentry__number')\
            #    .select_related()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('screens/playlist_view', args=[str(self.id)])
