from django.db import models


class Schedule(models.Model):
    name = models.TextField()
    description = models.TextField()
