import datetime
from unittest import TestCase

import time_machine
from django.db.models import ProtectedError

from screens.models import Playlist, PlaylistEntry, Source, PlaylistRelation

UTC = datetime.timezone.utc

def sources(playlist_entries):
    return list(map(lambda x: x.source, playlist_entries))


class PlaylistTests(TestCase):
    def setUp(self):
        self.base_time = datetime.datetime.fromisoformat("2022-03-27T20:59:34.000+00:00")
        time_machine.travel(self.base_time, tick=False).start()
        self.list_a = Playlist.objects.create(name="listA")
        self.entry_a = PlaylistEntry.objects.create(playlist=self.list_a, number=1, source=Source.objects.create()).source
        self.list_b = Playlist.objects.create(name="listB")
        self.entry_b = PlaylistEntry.objects.create(playlist=self.list_b, number=2, source=Source.objects.create()).source
        self.list_c = Playlist.objects.create(name="listC")
        self.entry_c = PlaylistEntry.objects.create(playlist=self.list_c, number=3, source=Source.objects.create()).source

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

    def test_deleting_a_parent_is_blocked(self):
        self.list_a.parents.add(self.list_b)
        self.assertRaises(ProtectedError, self.list_b.delete)
        self.list_a.delete()

    def test_time_locked_correctly(self):
        self.assertEqual(self.list_a.last_updated.astimezone(UTC), self.base_time.astimezone(UTC))

    def test_adding_a_source_updates_last_updated(self):
        update_time = datetime.datetime.fromisoformat("2022-03-28T21:59:34+00:00")
        time_machine.travel(update_time, tick=False).start()
        PlaylistEntry.objects.create(playlist=self.list_a, number=2, source=Source.objects.create())
        self.list_a.refresh_from_db()
        self.assertEqual(self.list_a.last_updated.astimezone(UTC), update_time.astimezone(UTC))

    def test_adding_a_parent_updates_last_updated(self):
        update_time = datetime.datetime.fromisoformat("2022-03-28T21:59:34+00:00")
        time_machine.travel(update_time, tick=False).start()
        PlaylistRelation.objects.create(inheriting_list=self.list_b, super_list=self.list_a)
        self.list_a.refresh_from_db()
        self.assertEqual(self.list_a.last_updated.astimezone(UTC), self.base_time.astimezone(UTC))
        self.list_b.refresh_from_db()
        self.assertEqual(self.list_b.last_updated.astimezone(UTC), update_time.astimezone(UTC))

    def test_adding_a_source_updates_childrens_last_updated(self):
        PlaylistRelation.objects.create(inheriting_list=self.list_b, super_list=self.list_a)
        update_time = datetime.datetime.fromisoformat("2022-03-28T21:59:34+00:00")
        time_machine.travel(update_time, tick=False).start()
        PlaylistEntry.objects.create(playlist=self.list_a, number=2, source=Source.objects.create())
        self.list_b.refresh_from_db()
        self.assertEqual(self.list_b.last_updated.astimezone(UTC), update_time.astimezone(UTC))

    def test_circular_parents_meta_times_update(self):
        self.list_a.parents.add(self.list_b)
        self.list_b.parents.add(self.list_a)
        self.list_a.meta_times_touch()
