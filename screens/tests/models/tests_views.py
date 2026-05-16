import datetime
from django.test import TestCase

import time_machine

from screens.models import Playlist, PlaylistEntry, Source, Screen, Schedule
from screens.views import render_playlist_json


def web_source(url):
    return Source.objects.create(type=Source.IFRAME, name="s", url=url)


class RenderPlaylistJsonTests(TestCase):
    def setUp(self):
        time_machine.travel(
            datetime.datetime.fromisoformat("2022-03-27T20:59:34+00:00"), tick=False).start()
        self.base = Playlist.objects.create(name="base")
        self.b1 = web_source("http://e/b1")
        PlaylistEntry.objects.create(playlist=self.base, number=1, source=self.b1, duration=7)

        self.pl_intersp = Playlist.objects.create(name="pl")
        self.p1 = web_source("http://e/p1")
        PlaylistEntry.objects.create(playlist=self.pl_intersp, number=1, source=self.p1)

        self.scr_intersp = Playlist.objects.create(name="scr")
        self.s1 = web_source("http://e/s1")
        PlaylistEntry.objects.create(playlist=self.scr_intersp, number=1, source=self.s1)

    def test_base_only(self):
        out = render_playlist_json(self.base)
        self.assertEqual(out["playlist"],
                         [{"src": "http://e/b1", "type": "FRM", "duration": 7}])
        self.assertIsNone(out["interspersed"]["playlist"])
        self.assertIsNone(out["interspersed"]["screen"])
        self.assertEqual(out["current_playlist"], self.base.pk)
        self.assertIsNone(out["screen_id"])

    def test_playlist_interspersed_stream(self):
        self.base.interspersed_playlist = self.pl_intersp
        self.base.interspersed_rate = 3
        self.base.save()
        out = render_playlist_json(self.base)
        self.assertEqual(out["interspersed"]["playlist"],
                         {"items": [{"src": "http://e/p1", "type": "FRM", "duration": 10}],
                          "rate": 3})
        self.assertIsNone(out["interspersed"]["screen"])

    def test_screen_interspersed_stream(self):
        self.base.interspersed_playlist = self.pl_intersp
        self.base.interspersed_rate = 2
        self.base.save()
        schedule = Schedule.objects.create(name="s", description="", default_playlist=self.base)
        screen = Screen.objects.create(name="scr", schedule=schedule, ip="1.2.3.4",
                                       interspersed_playlist=self.scr_intersp,
                                       interspersed_rate=4)
        out = render_playlist_json(self.base, screen=screen, screen_id=screen.id)
        self.assertEqual(out["interspersed"]["screen"],
                         {"items": [{"src": "http://e/s1", "type": "FRM", "duration": 10}],
                          "rate": 4})
        self.assertEqual(out["interspersed"]["playlist"]["rate"], 2)
        self.assertEqual(out["screen_id"], screen.id)

    def test_aggregate_last_updated_uses_newest(self):
        self.base.interspersed_playlist = self.pl_intersp
        self.base.save()
        schedule = Schedule.objects.create(name="s", description="", default_playlist=self.base)
        screen = Screen.objects.create(name="scr", schedule=schedule, ip="1.2.3.4",
                                       interspersed_playlist=self.scr_intersp)
        update_time = datetime.datetime.fromisoformat("2022-04-01T00:00:00+00:00")
        time_machine.travel(update_time, tick=False).start()
        self.scr_intersp.meta_times_touch()
        self.scr_intersp.refresh_from_db()
        out = render_playlist_json(self.base, screen=screen, screen_id=screen.id)
        # aggregate picks the newest of base / playlist-interspersed /
        # screen-interspersed last_updated (here the just-touched screen one),
        # rendered in local time exactly as the view does.
        self.assertEqual(
            datetime.datetime.fromisoformat(out["playlist_last_updated"]),
            self.scr_intersp.last_updated)
