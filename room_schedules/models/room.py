from django.db import models

from room_schedules.models import Venue


class Room(models.Model):
    name = models.CharField(max_length=100)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    artifax_id = models.IntegerField(unique=True)

    def __str__(self):
        return "{}: {}".format(self.pk, self.name)


