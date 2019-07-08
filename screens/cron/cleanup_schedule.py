from django_cron import CronJobBase, Schedule

from screens.models import ScheduleRule


class CleanUpSchedule(CronJobBase):
    RUN_EVERY_MINS = 24 * 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'screens.cleanup_schedule'

    def do(self):
        for rule in filter(lambda x: x.is_expired(), ScheduleRule.objects.all()):
            rule.delete()
