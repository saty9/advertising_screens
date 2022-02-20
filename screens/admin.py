from admin_ordering.admin import OrderableAdmin
from django.urls import re_path
from django.contrib import admin

from screens.forms import SourceBulkCreateForm, PlaylistAssigningSourceForm
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
    readonly_fields = ('image_preview',)
    list_display = ('name', 'playlist_names', 'created_at', "exclude_from_play_all")
    list_filter = (
        "exclude_from_play_all",
        PlaylistListFilter
    )

    def get_urls(self):
        urls = super(SourceDisplay, self).get_urls()
        my_urls = [
            re_path(r'^bulk_create/$', self.bulk_create_view),
        ]
        return my_urls + urls

    def bulk_create_view(self, request):
        request.bulk_create = True
        return super(SourceDisplay, self).changeform_view(request)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None and hasattr(request, "bulk_create") and request.bulk_create:  # TODO and bulk create permission
            kwargs['form'] = SourceBulkCreateForm
            self.exclude = ("file", "name")
        else:
            kwargs["form"] = PlaylistAssigningSourceForm
            self.exclude = ()
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        form.save(commit=True)

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
