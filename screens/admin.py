from django.contrib import admin

# Register your models here.
from screens.models import Playlist, Schedule, ScheduleBuilderDirective, Screen, Source

admin.site.register(Playlist)
admin.site.register(Schedule)
admin.site.register(ScheduleBuilderDirective)
admin.site.register(Screen)
admin.site.register(Source)
