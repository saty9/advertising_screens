import uuid
import hashlib

from PIL import Image

from advertising.settings import MAX_IMG_WIDTH, MAX_IMG_HEIGHT

from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.template.loader import get_template
from django.db.models.signals import pre_save, post_save, pre_delete


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
                            help_text="resolution of files should be 1920x1080, videos must be mp4")
    url = models.URLField(blank=True, verbose_name="Website Address", help_text="only required if website type")
    expires_at = models.DateTimeField(blank=True, null=True, default=None)
    valid_from = models.DateTimeField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    playlists = models.ManyToManyField("Playlist", related_name="sources", symmetrical=False,
                                       through="PlaylistEntry", through_fields=("source", "playlist"),
                                       help_text="All sources that would be played by these playlists will be included in this one too.",
                                       blank=True)


    def __str__(self):
        return self.name

    def clean(self):
        if hasattr(self, "bulk_create") and self.bulk_create:
            return
        if self.type in [self.IMAGE, self.VIDEO] and self.file.name is None:
            raise ValidationError({'file': "File cannot be blank for image or video type sources"})
        if self.type == self.VIDEO and self.file.name[-4:] != ".mp4":
            raise ValidationError({'file': "Video files must have .mp4 extensions"})
        if self.type == self.IMAGE:
            try:
                img = Image.open(self.file)
                if img.width > MAX_IMG_WIDTH or img.height > MAX_IMG_HEIGHT:
                    raise ValidationError({'file': f"Image resolution must be at most {MAX_IMG_WIDTH}x{MAX_IMG_HEIGHT}"})
            except Exception as e:
                raise ValidationError({'file': f"Error opening image file: {e}"})


    def src(self):
        if self.type in [self.IFRAME]:
            return self.url
        return self.file.url

    def image_preview(self):
        return get_template("screens/source_preview.html").render({"source": {"source": self}})

    image_preview.short_description = 'Preview'

    def playlist_names(self):
        result = set()
        for name in self.playlistentry_set.all().values_list("playlist__name", flat=True):
            result.add(name)
        for name in self.playlist_set.values_list("name", flat=True):
            result.add(name)
        return list(result)

    playlist_names.short_description = "Playlists"

    def full_clean(self, exclude=None, validate_unique=True):
        return super().full_clean(exclude, validate_unique)

    def meta_times_touch(self):
        for playlist in self.playlists.all():
            playlist.meta_times_touch()

@receiver(pre_save, sender=Source)
def set_orig_file_hash(sender, instance=None, raw=False, **kwargs):
    instance._orig = None
    if instance is None or raw:
        return

    instance._orig_file_hash = None
    try:
        orig = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    instance._orig = orig
    if orig.file:
        orig_hash = hashlib.sha1()
        with orig.file.open("rb") as f:
            orig_hash.update(f.read(20_000_000))
        instance._orig_file_hash = orig_hash.digest()

@receiver(post_save, sender=Source)
def source_updated(sender, instance=None, raw=False, **kwargs):
    if instance is None or raw:
        return

    if instance._orig is None:
        return

    def file_changed():
        if bool(instance._orig.file) != bool(instance.file):
            return True
        if not instance.file:
            return False

        instance_hash = hashlib.sha1()
        with instance.file.open("rb") as f:
            instance_hash.update(f.read(20_000_000))
        return instance._orig_file_hash != instance_hash.digest()

    if instance._orig.type != instance.type or\
            instance._orig.url != instance.url or\
            instance._orig.expires_at != instance.expires_at or\
            instance._orig.valid_from != instance.valid_from or\
            file_changed():
        #TODO handle expires at and valid from properly somehow
        instance.meta_times_touch()

@receiver(pre_delete, sender=Source)
def source_deleted(sender, instance, **kwargs):
    if instance is None:
        return

    instance.meta_times_touch()
