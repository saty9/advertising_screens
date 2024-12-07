import datetime

from django_cron import CronJobBase, Schedule

from screens.models import Source


class CleanUpSources(CronJobBase):
    RUN_EVERY_MINS = 5
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'screens.cleanup_sources'

    def do(self):
        Source.objects.filter(expires_at__lte=datetime.datetime.now()).delete()
