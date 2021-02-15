from django.db import models

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

