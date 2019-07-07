from django.db import models


class Source(models.Model):
    name = models.TextField()
    file = models.FileField()
