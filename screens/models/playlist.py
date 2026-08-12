from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


def flatten(t):
    return [item for sublist in t for item in sublist]


class Playlist(models.Model):
    name = models.TextField()
    description = models.TextField()
    interspersed_playlist = models.ForeignKey("self", null=True, default=None, on_delete=models.SET_NULL,
                                              blank=True, related_name="interspersed_into")
    interspersed_rate = models.PositiveIntegerField(
        default=1,
        help_text="number of base playlist items to play before one item from the interspersed playlist")
    last_updated = models.DateTimeField(auto_now=True)
    parents = models.ManyToManyField("self", related_name="children", symmetrical=False,
                                     through="PlaylistRelation", through_fields=("inheriting_list", "super_list"),
                                     help_text="All sources that would be played by these playlists will be included in this one too.", blank=True)

    def parent_sources(self, block_list):
        block_list.append(self.id)
        return flatten(map(lambda x: x.get_sources(block_list), self.parents.exclude(id__in=block_list)))

    def get_sources(self, block_list = None):
        if block_list is None:
            block_list = []

        now = timezone.now()
        return list(self.playlistentry_set.select_related("source")
                    .filter(Q(source__valid_from__lte=now) | Q(source__valid_from__isnull=True))
                    .filter(Q(source__expires_at__gte=now) | Q(source__expires_at__isnull=True))
                    .order_by('number')) + self.parent_sources(block_list)

    def meta_times_touch(self, block_list=None):
        if block_list is None:
            block_list = []
        block_list.append(self.id)
        self.last_updated = timezone.now()
        self.save()
        for child in self.children.exclude(id__in=block_list):
            child.meta_times_touch(block_list)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('screens/playlist_view', args=[str(self.id)])


@receiver(pre_delete, sender=Playlist)
def interspersed_referrers_touched(sender, instance=None, **kwargs):
    """
    Republish anything that was interspersing the playlist being deleted.
    """
    from .screen import Screen

    if instance is None:
        return
    for playlist in instance.interspersed_into.all():
        playlist.meta_times_touch()
    # Screen is imported lazily; screens.models.screen imports this module.
    Screen.objects \
        .filter(interspersed_playlist=instance) \
        .update(last_updated=timezone.now())
