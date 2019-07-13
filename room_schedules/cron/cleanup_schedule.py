import datetime
from django_cron import CronJobBase, Schedule

from room_schedules.models import Event


class CleanUpSchedule(CronJobBase):
    RUN_EVERY_MINS = 24 * 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'room_schedules.cleanup_schedule'

    def do(self):
        Event.objects.filter(start_time__lt=datetime.datetime.now() - datetime.timedelta(days=2))

