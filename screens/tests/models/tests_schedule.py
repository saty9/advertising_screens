from datetime import timedelta
from django.test import TestCase

import recurrence
from django.utils import timezone

from screens.models import Playlist, Schedule


class ScheduleTests(TestCase):

    def setUp(self):
        self.default_list = Playlist.objects.create()
        self.schedule = Schedule.objects.create(default_playlist=self.default_list)
        self.list_a = Playlist.objects.create()
        self.list_b = Playlist.objects.create()
        self.list_c = Playlist.objects.create()

    # ScheduleRule.starts/start_time/end_time are Date/Time fields holding civil
    # local wall-clock values, and Schedule.get_playlist evaluates django-recurrence
    # in naive local time. Under USE_TZ=True the wall clock is UTC, so fixtures must
    # use naive local time to model what production (admin input) actually stores.
    def _now(self):
        return timezone.localtime().replace(tzinfo=None)

    def make_current_daily_reccurence(self):
        rule = recurrence.Rule(recurrence.DAILY)
        return recurrence.Recurrence(
            dtstart=self._now() - timedelta(days=1),
            dtend=self._now() + timedelta(days=1),
            rrules=[rule]
        )

    def make_expired_daily_reccurence(self):
        rule = recurrence.Rule(recurrence.DAILY)
        return recurrence.Recurrence(
            dtstart=self._now() - timedelta(days=10),
            dtend=self._now() - timedelta(days=1),
            rrules=[rule]
        )

    def test_get_default_playlist(self):
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_single_rule(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=self._now(),
            start_time=self._now() - timedelta(minutes=1),
            end_time=self._now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    def test_get_single_rule_wrong_times(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=self._now(),
            start_time=self._now() + timedelta(minutes=1),
            end_time=self._now() - timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_expired_rule(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=self._now() - timedelta(days=1),
            start_time=self._now() - timedelta(minutes=1),
            end_time=self._now() + timedelta(minutes=1),
            occurrences=self.make_expired_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_future_rule(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=self._now() + timedelta(days=1),
            start_time=self._now() - timedelta(minutes=1),
            end_time=self._now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_priorities(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=10,
            starts=self._now() - timedelta(days=1),
            start_time=self._now() - timedelta(minutes=1),
            end_time=self._now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.schedule.schedulerule_set.create(
            playlist=self.list_b,
            priority=1,
            starts=self._now() - timedelta(days=1),
            start_time=self._now() - timedelta(minutes=1),
            end_time=self._now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_b)

