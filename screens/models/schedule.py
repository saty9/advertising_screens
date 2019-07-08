from django.db import models
from django.utils import timezone

from screens.models import Playlist


class Schedule(models.Model):
    name = models.TextField()
    description = models.TextField()
    default_playlist = models.ForeignKey(Playlist, on_delete=models.PROTECT)

    def get_playlist(self):
        from screens.models import SchedulePart
        part = SchedulePart.objects\
            .filter(schedule_builder__schedule=self, start_time__lte=timezone.now(), end_time__gt=timezone.now())\
            .order_by('priority').first()
        if part:
            return part
        else:
            return self.default_playlist
