from django.db import models

from screens.models.playlist import Playlist
from screens.models.schedule import Schedule
from screens.models.source import Source


class PlaylistEntry(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    number = models.IntegerField()
