from django.db import models

from screens.models import Playlist, ScheduleRule


class SchedulePart(models.Model):
    schedule_rule = models.ForeignKey(ScheduleRule, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    priority = models.IntegerField()
