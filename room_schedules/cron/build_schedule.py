from django_cron import CronJobBase, Schedule

from room_schedules.models import Venue
from room_schedules.settings import HOUR_BREAK_POINT


class BuildSchedule(CronJobBase):
    RUN_EVERY_MINS = 60
    RUN_AT_TIMES = ['{}:01'.format(HOUR_BREAK_POINT)]
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'room_schedules.build_schedule'

    def do(self):
        for venue in Venue.objects.all():
            venue.update_events()
