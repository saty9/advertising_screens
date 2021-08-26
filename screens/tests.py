from datetime import timedelta

import recurrence
from django.test import TestCase
from django.utils import timezone

from screens.models import Schedule, Playlist, PlaylistEntry, Source


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

    def test_get_single_rule_wrong_times(self):
        self.schedule.schedulerule_set.create(
            playlist=self.list_a,
            priority=1,
            starts=timezone.now(),
            start_time=timezone.now() + timedelta(minutes=1),
            end_time=timezone.now() - timedelta(minutes=1),
            occurrences=self.make_current_daily_reccurence()
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


def sources(playlist_entries):
    return list(map(lambda x: x.source, playlist_entries))


class PlaylistTests(TestCase):
    def setUp(self):
        self.list_a = Playlist.objects.create()
        self.entry_a = PlaylistEntry.objects.create(playlist=self.list_a, number=1, source=Source.objects.create()).source
        self.list_b = Playlist.objects.create()
        self.entry_b = PlaylistEntry.objects.create(playlist=self.list_b, number=1, source=Source.objects.create()).source
        self.list_c = Playlist.objects.create()
        self.entry_c = PlaylistEntry.objects.create(playlist=self.list_c, number=1, source=Source.objects.create()).source

    def test_simple_list(self):
        self.assertListEqual(sources(self.list_a.get_sources()), [self.entry_a])

    def test_single_inherit(self):
        self.list_a.parents.add(self.list_b)
        self.assertListEqual(sources(self.list_a.get_sources()), [self.entry_a, self.entry_b])

    def test_deep_inherit(self):
        self.list_a.parents.add(self.list_b)
        self.list_b.parents.add(self.list_c)
        self.assertListEqual(sources(self.list_a.get_sources()), [self.entry_a, self.entry_b, self.entry_c])

    def test_multi_inherit(self):
        self.list_a.parents.add(self.list_b, self.list_c)
        self.assertListEqual(sources(self.list_a.get_sources()), [self.entry_a, self.entry_b, self.entry_c])

    def test_circular_doesnt_spin(self):
        self.list_a.parents.add(self.list_b)
        self.list_b.parents.add(self.list_a)
        self.assertListEqual(sources(self.list_a.get_sources()), [self.entry_a, self.entry_b])
