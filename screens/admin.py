from django.contrib import admin

# Register your models here.
from screens.models import Playlist, Schedule, ScheduleRule, Screen, Source, PlaylistEntry


class PlaylistEntryInline(admin.TabularInline):
    model = PlaylistEntry
    extra = 3


class PlaylistDisplay(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description', 'interspersed_source']}),
    ]
    inlines = [PlaylistEntryInline]


class ScheduleRuleInline(admin.StackedInline):
    model = ScheduleRule
    extra = 1


class ScheduleDisplay(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description', 'default_playlist', 'is_default']}),
    ]
    inlines = [ScheduleRuleInline]


admin.site.register(Playlist, PlaylistDisplay)
admin.site.register(Schedule, ScheduleDisplay)
admin.site.register(ScheduleRule)
admin.site.register(Screen)
admin.site.register(Source)
admin.site.site_header = "Display Screen Admin"