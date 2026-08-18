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
        # Local (Europe/London) wall clock: `starts` is a DateField and
        # start_time/end_time are TimeFields keyed to civil time, and
        # django-recurrence works in naive datetime space — so strip tz.
        now = timezone.localtime().replace(tzinfo=None)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        playlist = self.default_playlist
        # Fetch rules that have already started; time-window filtering is done
        # in Python so that overnight rules (start_time > end_time) are handled
        # correctly — the DB filter cannot express a window that wraps midnight.
        for rule in self.schedulerule_set.filter(starts__lte=now).order_by('priority', 'pk').all():
            overnight = rule.start_time > rule.end_time
            if overnight:
                in_window = now.time() >= rule.start_time or now.time() <= rule.end_time
            else:
                in_window = rule.start_time <= now.time() <= rule.end_time
            if not in_window:
                continue

            if overnight and now.time() <= rule.end_time:
                # Rule's occurrence was yesterday
                ref_start = yesterday_start
                ref_end = today_start
            else:
                ref_start = today_start
                ref_end = today_start + timedelta(days=1)

            ref_start -= timedelta(seconds=1) # between is exclusive and date based so we need to be just before midnight if start time was midnight

            # Normalize the stored dtstart to naive local civil time so that
            # dateutil generates naive occurrence datetimes that can be compared
            # with ref_start/ref_end.  RecurrenceField serializes dtstart as UTC
            # so we must convert back to local time before passing to between().
            stored_dtstart = rule.occurrences.dtstart
            if stored_dtstart is not None and stored_dtstart.tzinfo is not None:
                normalized_dtstart = timezone.localtime(stored_dtstart).replace(tzinfo=None)
            else:
                normalized_dtstart = stored_dtstart or ref_start
            if any(rule.occurrences.between(ref_start, ref_end, dtstart=normalized_dtstart)):
                return rule.playlist

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
