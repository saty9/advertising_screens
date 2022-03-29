from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from screens.models import Playlist


class PlaylistRelation(models.Model):
    super_list = models.ForeignKey(Playlist, on_delete=models.PROTECT, related_name="children_list", verbose_name="Parent") #limit_choices_to
    inheriting_list = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="parents_list")

    def __str__(self):
        return f"{self.inheriting_list} inherits from {self.super_list}"


@receiver(pre_save, sender=PlaylistRelation)
def source_updated(sender, instance=None, raw=False, **kwargs):
    if instance is None or raw:
        return

    instance.inheriting_list.meta_times_touch()
