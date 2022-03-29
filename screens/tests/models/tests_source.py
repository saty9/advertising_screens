import datetime
from unittest import TestCase

import time_machine
from django.core.files.uploadedfile import SimpleUploadedFile

from screens.models import Playlist, PlaylistEntry, Source

UTC = datetime.timezone.utc
update_time = datetime.datetime.fromisoformat("2022-03-28T20:59:34.000+00:00")

class SourceTests(TestCase):
    def setUp(self):
        self.base_time = datetime.datetime.fromisoformat("2022-03-27T20:59:34.000+00:00")
        time_machine.travel(self.base_time, tick=False).start()
        self.playlist = Playlist.objects.create(name="listA")
        self.source = Source.objects.create()
        self.pl_entry = PlaylistEntry.objects.create(playlist=self.playlist, number=1, source=self.source)

    @time_machine.travel(update_time, tick=False)
    def test_updating_file_updates_playlist_last_updated(self):
        self.source.file = SimpleUploadedFile("test_file.png", b"an image")
        self.source.save()
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.last_updated.astimezone(UTC), update_time.astimezone(UTC))

    @time_machine.travel(update_time, tick=False)
    def test_updating_name_does_not_update_playlist_last_updated(self):
        self.assertEqual(self.playlist.last_updated.astimezone(UTC), self.base_time.astimezone(UTC))
        self.source.name = "new name"
        self.source.save()
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.last_updated.astimezone(UTC), self.base_time.astimezone(UTC))

    @time_machine.travel(update_time, tick=False)
    def test_updating_url_updates_playlist_last_updated(self):
        self.source.url = "new url"
        self.source.save()
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.last_updated.astimezone(UTC), update_time.astimezone(UTC))
