from django.db import models
from django.urls import reverse

from screens.models import Source
from screens.models.schedule import Schedule


class Screen(models.Model):
    name = models.TextField()
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, null=True)
    interspersed_source = models.ForeignKey(Source,
                                            null=True,
                                            default=None,
                                            on_delete=models.SET_NULL,
                                            blank=True,
                                            help_text="Optional (you probably want an event schedule here)")
    ip = models.GenericIPAddressField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('screens/screen_view', args=[str(self.id)])
