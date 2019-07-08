from django.db import models

from screens.models import Playlist, ScheduleBuilderDirective


class SchedulePart(models.Model):
    schedule_builder = models.ForeignKey(ScheduleBuilderDirective, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    priority = models.IntegerField()
