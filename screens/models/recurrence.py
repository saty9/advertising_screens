from django.db import models
from django.core.validators import int_list_validator

from screens.models.schedule_builder_directive import ScheduleBuilderDirective


class Recurrence(models.Model):
    WEEKLY = 'W'
    MONTHLY = 'M'
    YEARLY = 'Y'
    types = (
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    )
    schedule_builder = models.ForeignKey(to=ScheduleBuilderDirective, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=types)
    on = models.CharField(validators=[int_list_validator], max_length=100)
    every = models.IntegerField(default=1)  # used if every 2 weeks instead of every week
