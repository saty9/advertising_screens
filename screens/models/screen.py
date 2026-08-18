from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from screens.models.schedule import Schedule


class Screen(models.Model):
    name = models.TextField()
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, null=True)
    interspersed_playlist = models.ForeignKey("Playlist",
                                              null=True,
                                              default=None,
                                              on_delete=models.SET_NULL,
                                              blank=True,
                                              related_name="+",
                                              help_text="Optional playlist interspersed into the screen's playlist")
    interspersed_rate = models.PositiveIntegerField(
        default=1,
        help_text="number of items to play before one item from the interspersed playlist")
    ip = models.GenericIPAddressField()
    last_seen = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True) # Manually tracked to avoid last_seen constantly bumping this
    
    def online(self):
        return self.last_seen and self.last_seen >= timezone.now()-timedelta(minutes=1)
    online.boolean = True

    def screen_preview(self):
        if self.id:
            return get_template("screens/screen_preview.html").render({"screen_url": self.get_absolute_url()})

    screen_preview.short_description = 'Preview'
        

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('screens/screen_view', args=[str(self.id)])
