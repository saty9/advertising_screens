import datetime
from celery import shared_task
from django.utils import timezone
from django.db.models import F
from screens.models import Source, ScheduleRule

@shared_task(name='screens.tasks.cleanup_sources')
def cleanup_sources():
    Source.objects.filter(expires_at__lte=datetime.datetime.now()).delete()

@shared_task(name='screens.tasks.update_playlists')
def update_playlists():
    # Find sources with playlists whose last_updated (meta time) is less than the source's valid_from
    sources_to_update = Source.objects.filter(
        valid_from__isnull=False,
        playlists__last_updated__lt=F('valid_from'),
        valid_from__lte=timezone.now()
    ).distinct()
    
    for source in sources_to_update:
        print(f"Updating playlists for source {source}")
        source.meta_times_touch()

@shared_task(name='screens.tasks.cleanup_schedule')
def cleanup_schedule():
    for rule in filter(lambda x: x.is_expired(), ScheduleRule.objects.all()):
        rule.delete()
