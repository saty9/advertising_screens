from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from screens.models.source import Source


class PlaylistEntry(models.Model):
    playlist = models.ForeignKey("Playlist", on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    number = models.IntegerField()
    duration = models.IntegerField(default=10, null=True, blank=True,
                                   help_text="number of seconds to display source for (ignored for videos)")

    class Meta:
        ordering = ['number']

    def __str__(self):
        return ""


@receiver(pre_delete, sender=PlaylistEntry)
@receiver(pre_save, sender=PlaylistEntry)
def entry_updated(sender, instance=None, raw=False, **kwargs):
    if instance is None or raw:
        return

    instance.playlist.meta_times_touch()
