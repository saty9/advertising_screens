from django.db import models


class Playlist(models.Model):
    name = models.TextField()
    description = models.TextField()
    plays_everything = models.BooleanField(default=False)

    def get_sources(self):
        from screens.models import Source
        if self.plays_everything:
            return Source.objects.all()
        else:
            return Source.objects.filter(playlistentry__playlist=self).order_by('playlistentry__number')

    def __str__(self):
        return self.name
