from datetime import datetime

from django.db.models.signals import post_save, pre_save
from django.dispatch import Signal, receiver
from django.utils import timezone

from django.db import models
from recurrence.fields import RecurrenceField

from screens.models.playlist import Playlist
from screens.models.schedule import Schedule


class ScheduleRule(models.Model):
    playlist = models.ForeignKey(to=Playlist, on_delete=models.CASCADE)
    schedule = models.ForeignKey(to=Schedule, on_delete=models.CASCADE)
    starts = models.DateField()
    occurrences = RecurrenceField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    priority = models.IntegerField()

    def is_expired(self):
        return not bool(self.occurrences.after(timezone.datetime.today() - timezone.timedelta(days=2), inc=True))


@receiver(pre_save, sender=ScheduleRule)
def before_save(sender, **kwargs):
    if kwargs['instance'].end_time == datetime.min.time():
        kwargs['instance'].end_time = datetime.max.time()
