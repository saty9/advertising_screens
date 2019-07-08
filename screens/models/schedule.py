from django.db import models
from django.utils import timezone

from screens.models import Playlist


class Schedule(models.Model):
    name = models.TextField()
    description = models.TextField()
    default_playlist = models.ForeignKey(Playlist, on_delete=models.PROTECT)
    is_default = models.BooleanField(default=False)

    def get_playlist(self):
        from screens.models import SchedulePart
        part = SchedulePart.objects\
            .filter(schedule_rule__schedule=self, start_time__lte=timezone.now(), end_time__gt=timezone.now())\
            .order_by('priority').first()
        if part:
            return part.playlist
        else:
            return self.default_playlist

    @staticmethod
    def get_default():
        out = Schedule.objects.filter(is_default=True).first()
        if out:
            return out
        else:
            return None

    def __str__(self):
        return self.name
