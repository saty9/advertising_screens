from django.db import models


class Playlist(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name
