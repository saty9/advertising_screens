from django.contrib import admin

# Register your models here.
from screens.models import Playlist, Schedule, ScheduleRule, Screen, Source, PlaylistEntry


class PlaylistEntryInline(admin.TabularInline):
    model = PlaylistEntry
    extra = 3


class PlaylistDisplay(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description']}),
    ]
    inlines = [PlaylistEntryInline]


admin.site.register(Playlist, PlaylistDisplay)
admin.site.register(Schedule)
admin.site.register(ScheduleRule)
admin.site.register(Screen)
admin.site.register(Source)
