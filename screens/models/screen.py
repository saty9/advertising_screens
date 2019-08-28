from django.db import models
from django.urls import reverse

from screens.models.schedule import Schedule


class Screen(models.Model):
    name = models.TextField()
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, null=True)
    ip = models.GenericIPAddressField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('screens/screen_view', args=[str(self.id)])
