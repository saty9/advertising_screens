from django.db import models

from screens.models import Playlist


class PlaylistRelation(models.Model):
    super_list = models.ForeignKey(Playlist, on_delete=models.PROTECT, related_name="children_list", verbose_name="Parent") #limit_choices_to
    inheriting_list = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="parents_list")

    def __str__(self):
        return f"{self.inheriting_list} inherits from {self.super_list}"
