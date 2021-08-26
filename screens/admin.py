from admin_ordering.admin import OrderableAdmin
from django.contrib import admin

# Register your models here.
from screens.models import Playlist, Schedule, ScheduleRule, Screen, Source, PlaylistEntry


class PlaylistEntryInline(OrderableAdmin, admin.TabularInline):
    model = PlaylistEntry
    ordering_field = 'number'


class PlaylistDisplay(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description', 'interspersed_source', 'plays_everything', "parents"]}),
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


class SourceDisplay(admin.ModelAdmin):
    readonly_fields = ('image_preview', 'playlist_names')
    list_display = ('name', 'playlist_names', 'created_at')
    class Media:
        js = (
            "admin/js/jquery.init.js",
            'screens/js/source_form.js',
        )

class ScreenAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'online', 'last_seen')
    
    


admin.site.register(Playlist, PlaylistDisplay)
admin.site.register(Schedule, ScheduleDisplay)
admin.site.register(ScheduleRule)
admin.site.register(Screen, ScreenAdmin)
admin.site.register(Source, SourceDisplay)
admin.site.site_header = "Display Screen Admin"
