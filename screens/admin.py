from admin_ordering.admin import OrderableAdmin
from django.contrib import admin

# Register your models here.
from screens.models import Playlist, Schedule, ScheduleRule, Screen, Source, PlaylistEntry


class PlaylistEntryInline(OrderableAdmin, admin.TabularInline):
    model = PlaylistEntry
    ordering_field = 'number'


class PlaylistParentsInline(admin.TabularInline):
    model = Playlist.parents.through
    fk_name = "inheriting_list"
    verbose_name_plural = "Playlists to inherit from"
    verbose_name = "Parent List"
    extra = 1


class PlaylistDisplay(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description', 'interspersed_source', 'plays_everything']}),
    ]
    inlines = [PlaylistParentsInline, PlaylistEntryInline]


class ScheduleRuleInline(admin.StackedInline):
    model = ScheduleRule
    extra = 1


class ScheduleDisplay(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description', 'default_playlist', 'is_default']}),
    ]
    inlines = [ScheduleRuleInline]


class PlaylistListFilter(admin.SimpleListFilter):
    title = "In Playlist"
    parameter_name = "playlist"

    def lookups(self, request, model_admin):
        return Playlist.objects.values_list("id", "name")

    def queryset(self, request, queryset):
        return queryset.filter(playlist__id=self.value()) or queryset.filter(playlistentry__playlist__id=self.value())


class SourceDisplay(admin.ModelAdmin):
    readonly_fields = ('image_preview', 'playlist_names')
    list_display = ('name', 'playlist_names', 'created_at', "exclude_from_play_all")
    list_filter = (
        "exclude_from_play_all",
        PlaylistListFilter
    )
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
