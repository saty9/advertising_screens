from datetime import timedelta, time, date, datetime
from django.test import TestCase

import recurrence
import time_machine
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

    # --- overnight / adjacent-day rule tests ---

    def _make_daily_since(self, since: datetime):
        rule = recurrence.Rule(recurrence.DAILY)
        return recurrence.Recurrence(
            dtstart=since,
            rrules=[rule]
        )

    @time_machine.travel("2024-06-15 23:30:00", tick=False)
    def test_overnight_rule_active_before_midnight(self):
        """A rule whose window straddles midnight should match before midnight."""
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(23, 0),
            end_time=time(1, 0),
            occurrences=self._make_daily_since(datetime(2024, 6, 1)),
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    @time_machine.travel("2024-06-16 00:30:00", tick=False)
    def test_overnight_rule_active_after_midnight(self):
        """A rule whose window straddles midnight should still match after midnight."""
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(23, 0),
            end_time=time(1, 0),
            occurrences=self._make_daily_since(datetime(2024, 6, 1)),
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    @time_machine.travel("2024-06-15 12:00:00", tick=False)
    def test_overnight_rule_inactive_midday(self):
        """A rule whose window straddles midnight should not match in the middle of the day."""
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(23, 0),
            end_time=time(1, 0),
            occurrences=self._make_daily_since(datetime(2024, 6, 1)),
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    @time_machine.travel("2024-06-15 01:30:00", tick=False)
    def test_overnight_rule_inactive_just_after_end(self):
        """A rule ending at 01:00 should not match at 01:30."""
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(23, 0),
            end_time=time(1, 0),
            occurrences=self._make_daily_since(datetime(2024, 6, 1)),
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    @time_machine.travel("2024-06-17 12:00:00", tick=False)  # Monday
    def test_weekly_rule_does_not_fire_the_day_before(self):
        """A weekly rule whose next occurrence is tomorrow must not fire today.

        Previously, because get_playlist passed dtstart=yesterday to between(),
        the weekly recurrence was shifted to fire on yesterday's weekday, which
        could cause the occurrence check to produce false results for rules whose
        stored dtstart day-of-week differs from yesterday.  This test fixes the
        case where the time window matches but the recurrence day does not.
        """
        # dtstart June 4 (Tuesday) → fires every Tuesday (Jun 11, 18, 25 …)
        # We are on Monday Jun 17; next Tuesday is tomorrow Jun 18.
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(11, 0),
            end_time=time(13, 0),
            occurrences=recurrence.Recurrence(
                dtstart=datetime(2024, 6, 4),  # Tuesday
                rrules=[recurrence.Rule(recurrence.WEEKLY)],
            ),
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    @time_machine.travel("2024-06-18 12:00:00", tick=False)  # Tuesday
    def test_weekly_rule_fires_on_correct_day(self):
        """A weekly Tuesday rule must fire when today is Tuesday."""
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(11, 0),
            end_time=time(13, 0),
            occurrences=recurrence.Recurrence(
                dtstart=datetime(2024, 6, 4),  # Tuesday
                rrules=[recurrence.Rule(recurrence.WEEKLY)],
            ),
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    @time_machine.travel("2024-06-19 00:30:00", tick=False)  # Wednesday 00:30
    def test_weekly_overnight_rule_active_after_midnight(self):
        """A weekly overnight Tuesday rule (23:00–01:00) is still active on Wednesday 00:30."""
        # dtstart June 4 (Tuesday) → fires Tuesdays 23:00 through Wednesday 01:00
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(23, 0),
            end_time=time(1, 0),
            occurrences=recurrence.Recurrence(
                dtstart=datetime(2024, 6, 4),  # Tuesday
                rrules=[recurrence.Rule(recurrence.WEEKLY)],
            ),
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    @time_machine.travel("2024-06-20 00:30:00", tick=False)  # Thursday 00:30
    def test_weekly_overnight_rule_inactive_wrong_day_after_midnight(self):
        """A weekly overnight Tuesday rule must not fire on Thursday 00:30."""
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=date(2024, 6, 1),
            start_time=time(23, 0),
            end_time=time(1, 0),
            occurrences=recurrence.Recurrence(
                dtstart=datetime(2024, 6, 4),  # Tuesday
                rrules=[recurrence.Rule(recurrence.WEEKLY)],
            ),
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)


@time_machine.travel("2024-06-18 12:00:00", tick=False)  # Tuesday
def test_byday_rule_fires_on_correct_day(self):
    """A rule using BYDAY=TU should fire when today is Tuesday."""
    self.schedule.schedulerule_set.create(
        playlist=self.list_a,
        priority=1,
        starts=date(2024, 6, 1),
        start_time=time(11, 0),
        end_time=time(13, 0),
        occurrences=recurrence.Recurrence(
            dtstart=datetime(2024, 6, 1),
            rrules=[recurrence.Rule(
                recurrence.WEEKLY,
                byday=[recurrence.Weekday(recurrence.TUESDAY)],
            )],
        ),
    )
    self.assertEqual(self.schedule.get_playlist(), self.list_a)

@time_machine.travel("2024-06-17 12:00:00", tick=False)  # Monday
def test_byday_rule_does_not_fire_on_wrong_day(self):
    """A rule using BYDAY=TU should not fire when today is Monday."""
    self.schedule.schedulerule_set.create(
        playlist=self.list_a,
        priority=1,
        starts=date(2024, 6, 1),
        start_time=time(11, 0),
        end_time=time(13, 0),
        occurrences=recurrence.Recurrence(
            dtstart=datetime(2024, 6, 1),
            rrules=[recurrence.Rule(
                recurrence.WEEKLY,
                byday=[recurrence.Weekday(recurrence.TUESDAY)],
            )],
        ),
    )
    self.assertEqual(self.schedule.get_playlist(), self.default_list)

