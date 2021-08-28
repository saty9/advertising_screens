from datetime import timedelta

import recurrence
from django.test import TestCase
from django.utils import timezone

from screens.models import Schedule, Playlist


class ScheduleTests(TestCase):

    def setUp(self):
        self.default_list = Playlist.objects.create()
        self.schedule = Schedule.objects.create(default_playlist=self.default_list)
        self.list_a = Playlist.objects.create()
        self.list_b = Playlist.objects.create()
        self.list_c = Playlist.objects.create()

    def make_current_daily_reccurence(self):
        rule = recurrence.Rule(recurrence.DAILY)
        return recurrence.Recurrence(
            dtstart=timezone.now() - timedelta(days=1),
            dtend=timezone.now() + timedelta(days=1),
            rrules=[rule]
        )

    def make_single_occurence(self, date):
        return recurrence.Recurrence(
            rdates=[date]
        )

    def make_expired_daily_reccurence(self):
        rule = recurrence.Rule(recurrence.DAILY)
        return recurrence.Recurrence(
            dtstart=timezone.now() - timedelta(days=10),
            dtend=timezone.now() - timedelta(days=1),
            rrules=[rule]
        )

    def test_get_default_playlist(self):
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_single_rule(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() - timedelta(minutes=1),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    def test_get_single_rule_before_start_time(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() + timedelta(minutes=1),
            end_time=timezone.now() + timedelta(minutes=2),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_single_rule_after_end_time(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() - timedelta(minutes=2),
            end_time=timezone.now() - timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_single_rule_wrapping_times_on_date_before_start(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() + timedelta(minutes=5),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_single_occurence(timezone.now())
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_single_rule_wrapping_times_on_date_after_start(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() - timedelta(minutes=1),
            end_time=timezone.now() - timedelta(minutes=5),
            occurrences=self.make_single_occurence(timezone.now())
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    def test_get_single_rule_wrapping_times_on_day_after_before_end(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now() - timedelta(days=1),
            start_time=timezone.now() + timedelta(minutes=5),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_single_occurence(timezone.now() - timedelta(days=1))
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_a)

    def test_get_single_rule_wrapping_times_on_day_after_after_end(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() - timedelta(minutes=5),
            end_time=timezone.now() - timedelta(minutes=1),
            occurrences=self.make_single_occurence(timezone.now() - timedelta(days=1))
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_single_rule_wrapping_times_on_start_date_of_daily_before_end(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() + timedelta(minutes=5),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_single_rule_occurrence_yesterday(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now() - timedelta(days=1),
            start_time=timezone.now() - timedelta(minutes=5),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_single_occurence(timezone.now()-timedelta(days=1))
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_expired_rule(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now() - timedelta(days=1),
            start_time=timezone.now() - timedelta(minutes=1),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_expired_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_get_future_rule(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now() + timedelta(days=1),
            start_time=timezone.now() - timedelta(minutes=1),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.default_list)

    def test_priorities(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=10,
            starts=timezone.now() - timedelta(days=1),
            start_time=timezone.now() - timedelta(minutes=1),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.schedule.schedulerule_set.create(
            playlist=self.list_b,
            priority=1,
            starts=timezone.now() - timedelta(days=1),
            start_time=timezone.now() - timedelta(minutes=1),
            end_time=timezone.now() + timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
        )
        self.assertEqual(self.schedule.get_playlist(), self.list_b)
