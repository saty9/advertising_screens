import os
import uuid

from django.core.exceptions import ValidationError
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
        (IFRAME, 'Website'),
    )
    type = models.CharField(max_length=3, choices=types)
    name = models.TextField()
    file = models.FileField(upload_to=get_file_path,
                            null=True,
                            blank=True,
                            help_text="resolution of files should be 1360x768, videos must be mp4")
    url = models.URLField(blank=True, verbose_name="Website Address", help_text="only required if website type")
    exclude_from_play_all = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True, default=None)
    valid_from = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    def clean(self):
        if self.type in [self.IMAGE, self.VIDEO] and self.file.name is None:
            raise ValidationError({'file': "File cannot be blank for image or video type sources"})
        if self.type == self.VIDEO and self.file.name[-4:] != ".mp4":
            raise ValidationError({'file': "Video files must have .mp4 extensions"})

    def src(self):
        if self.type in [self.IFRAME]:
            return self.url
        return self.file.url
