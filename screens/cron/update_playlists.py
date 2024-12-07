import datetime

from django.utils import timezone
from django_cron import CronJobBase, Schedule
from django_cron.models import CronJobLog

from screens.models import Source


class UpdatePlaylists(CronJobBase):
    RUN_EVERY_MINS = 5
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'screens.update_playlists'

    def do(self):
        query = CronJobLog.objects.filter(code=self.code, is_success=True)
        if query.exists():
            last_job_start = query.latest('start_time').start_time
        else:
            last_job_start = timezone.now() - datetime.timedelta(days=365)
        for source in Source.objects.filter(valid_from__gte=last_job_start, valid_from__lte=timezone.now()):
            print(f"Updating playlists for source {source}")
            source.meta_times_touch()
