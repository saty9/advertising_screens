from django.db import models

from screens.models.playlist import Playlist
from screens.models.schedule import Schedule


class ScheduleBuilderDirective(models.Model):
    playlist = models.ForeignKey(to=Playlist, on_delete=models.CASCADE)
    schedule = models.ForeignKey(to=Schedule, on_delete=models.CASCADE)
    ends = models.DateField()
    starts = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    priority = models.IntegerField()

