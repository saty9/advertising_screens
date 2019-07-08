import os
import uuid

from django.db import models


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename


class Source(models.Model):
    IMAGE = 'IMG'
    VIDEO = 'VID'
    IFRAME = 'FRM'
    types = (
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
        (IFRAME, 'IFrame'),
    )
    type = models.CharField(max_length=3, choices=types)
    name = models.TextField()
    file = models.FileField(upload_to=get_file_path,
                            null=True,
                            blank=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name
