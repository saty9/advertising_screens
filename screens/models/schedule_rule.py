from datetime import timedelta, datetime

from django.db.models.signals import pre_save
from django.dispatch import receiver
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
    start_time = models.TimeField(help_text="Matching start and end times will create the end time 1 second before the start time")
    end_time = models.TimeField(help_text="End times before the start time will wrap around into the day after")
    priority = models.IntegerField()

    def is_expired(self):
        return not bool(self.occurrences.after(timezone.datetime.today() - timezone.timedelta(days=2), inc=True))


@receiver(pre_save, sender=ScheduleRule)
def before_save(sender, **kwargs):
    if kwargs['instance'].start_time == kwargs['instance'].end_time:
        end_time = datetime.combine(timezone.now().date(), kwargs['instance'].end_time) - timedelta(seconds=1)
        kwargs['instance'].end_time = end_time.time()
