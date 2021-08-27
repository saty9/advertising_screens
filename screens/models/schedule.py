from django.db import models
from django.utils import timezone
from datetime import timedelta

from screens.models import Playlist


class Schedule(models.Model):
    name = models.TextField()
    description = models.TextField()
    default_playlist = models.ForeignKey(Playlist, on_delete=models.PROTECT)
    is_default = models.BooleanField(default=False)

    def get_playlist(self):
        yesterday = timezone.now() - timedelta(days=1)
        tomorrow = timezone.now() + timedelta(days=1)
        playlist = self.default_playlist
        priority = 999999
        now = timezone.now()
        for rule in self.schedulerule_set.filter(starts__lte=now, start_time__lte=now.time(), end_time__gte=now.time()).all():
            if rule.priority > priority:
                continue
            if any(rule.occurrences.between(yesterday, tomorrow, dtstart=yesterday)):
                playlist = rule.playlist
                priority = rule.priority

        return playlist

    @staticmethod
    def get_default():
        out = Schedule.objects.filter(is_default=True).first()
        if out:
            return out
        else:
            return None

    def __str__(self):
        return self.name
