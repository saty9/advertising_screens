from unittest import TestCase

from django.db.models import ProtectedError

from screens.models import Playlist, PlaylistEntry, Source


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

    def test_deleting_a_parent_is_blocked(self):
        self.list_a.parents.add(self.list_b)
        self.assertRaises(ProtectedError, self.list_b.delete)
        self.list_a.delete()
