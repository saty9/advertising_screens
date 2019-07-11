from django_cron import CronJobBase, Schedule
from django.utils import timezone

from screens.models import ScheduleRule


class BuildSchedule(CronJobBase):
    RUN_EVERY_MINS = 24 * 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'screens.build_schedule'

    def do(self):
        today = timezone.now()
        upper_bound = today + timezone.timedelta(days=7)
        for rule in ScheduleRule.objects.filter(starts__lt=upper_bound):
            rule.generate_parts(7)

    def is_expired(self):
        pass
