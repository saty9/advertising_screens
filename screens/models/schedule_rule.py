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

    def generate_parts(self, days_in_advance=7):
        now = timezone.now()
        occurrences = self.occurrences.between(datetime.combine(self.starts, datetime.min.time()),
                                               now + timezone.timedelta(days=days_in_advance),
                                               inc=True)
        for x in occurrences:
            if self.end_time < self.start_time:
                self.schedulepart_set.create(playlist=self.playlist,
                                             start_time=timezone.datetime.combine(x, self.start_time),
                                             end_time=timezone.datetime.combine(x, datetime.max.time()),
                                             priority=self.priority)
                self.schedulepart_set.create(playlist=self.playlist,
                                             start_time=timezone.datetime.combine(x + timezone.timedelta(days=1), datetime.min.time()),
                                             end_time=timezone.datetime.combine(x + timezone.timedelta(days=1), self.end_time),
                                             priority=self.priority)
            else:
                self.schedulepart_set.create(playlist=self.playlist,
                                             start_time=timezone.datetime.combine(x, self.start_time),
                                             end_time=timezone.datetime.combine(x, self.end_time),
                                             priority=self.priority)

    def regenerate_parts(self):
        self.schedulepart_set.all().delete()
        self.generate_parts()

    def is_expired(self):
        return not bool(self.occurrences.after(timezone.datetime.today() - timezone.timedelta(days=2), inc=True))


@receiver(post_save, sender=ScheduleRule)
def on_save(sender, **kwargs):
    kwargs['instance'].regenerate_parts()


@receiver(pre_save, sender=ScheduleRule)
def before_save(sender, **kwargs):
    if kwargs['instance'].end_time == datetime.min.time():
        kwargs['instance'].end_time = datetime.max.time()
