from admin_ordering.admin import OrderableAdmin
from django.urls import re_path
from django.contrib import admin
from django.template.response import TemplateResponse
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display

from screens.forms import SourceBulkCreateForm, PlaylistAssigningSourceForm
from screens.models import Playlist, Schedule, ScheduleRule, Screen, Source, PlaylistEntry


class PlaylistEntryInline(OrderableAdmin, TabularInline):
    model = PlaylistEntry
    ordering_field = 'number'
    extra = 0
    fields = ('number', 'source', 'duration')


class PlaylistParentsInline(TabularInline):
    model = Playlist.parents.through
    fk_name = "inheriting_list"
    verbose_name_plural = "Playlists to inherit from"
    verbose_name = "Parent List"
    extra = 0


@admin.register(Playlist)
class PlaylistDisplay(ModelAdmin):
    list_display = ('name', 'show_source_count', 'plays_everything', 'last_updated')
    search_fields = ('name', 'description')
    list_filter = ('plays_everything',)
    readonly_fields = ('last_updated',)
    fieldsets = [
        (None, {'fields': ['name', 'description', 'plays_everything', 'interspersed_source', 'last_updated']}),
    ]
    inlines = [PlaylistParentsInline, PlaylistEntryInline]

    @display(description="Sources")
    def show_source_count(self, obj):
        return obj.playlistentry_set.count()

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'^tree/$', self.admin_site.admin_view(self.playlist_tree_view), name='screens_playlist_tree'),
        ]
        return my_urls + urls

    def playlist_tree_view(self, request):
        context = self.admin_site.each_context(request)
        context['title'] = 'Playlist Inheritance'
        context['is_fullwidth'] = "1"
        return TemplateResponse(request, 'admin/screens/playlist_tree.html', context)


class ScheduleRuleInline(StackedInline):
    model = ScheduleRule
    extra = 0
    fields = ('playlist', 'starts', 'occurrences', 'start_time', 'end_time', 'priority')


@admin.register(Schedule)
class ScheduleDisplay(ModelAdmin):
    list_display = ('name', 'default_playlist', 'is_default')
    search_fields = ('name', 'description')
    list_filter = ('is_default',)
    list_select_related = ('default_playlist',)
    fieldsets = [
        (None, {'fields': ['name', 'description', 'default_playlist', 'is_default']}),
    ]
    inlines = [ScheduleRuleInline]


class PlaylistListFilter(admin.SimpleListFilter):
    title = "In Playlist"
    parameter_name = "playlist"

    def lookups(self, request, model_admin):
        return Playlist.objects.values_list("id", "name")

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(playlistentry__playlist__id=self.value())


@admin.register(Source)
class SourceDisplay(ModelAdmin):
    readonly_fields = ('image_preview',)
    list_display = ('name', 'show_type', 'resolution', 'created_by', 'playlist_names', 'created_at', 'valid_from', 'expires_at')
    list_filter = (PlaylistListFilter, 'type')
    search_fields = ('name',)
    date_hierarchy = 'created_at'

    @display(description="Type", label={
        "Image": "success",
        "Video": "warning",
        "Website": "info",
    })
    def show_type(self, obj):
        return obj.get_type_display()

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'^bulk_create/$', self.bulk_create_view, name='screens_source_bulk_create'),
        ]
        return my_urls + urls

    def bulk_create_view(self, request):
        request.bulk_create = True
        return super().changeform_view(request)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None and hasattr(request, "bulk_create") and request.bulk_create:  # TODO and bulk create permission
            kwargs['form'] = SourceBulkCreateForm
            self.exclude = ("file", "name")
        else:
            kwargs["form"] = PlaylistAssigningSourceForm
            self.exclude = ()
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        form.save(commit=True)

    class Media:
        js = (
            "admin/js/jquery.init.js",
            'screens/js/source_form.js',
        )


@admin.register(Screen)
class ScreenAdmin(ModelAdmin):
    readonly_fields = ('screen_preview',)
    list_display = ('name', 'ip', 'show_online', 'last_seen', 'schedule')
    search_fields = ('name', 'ip')
    list_filter = ('schedule',)
    list_select_related = ('schedule',)

    @display(description="Online", boolean=True)
    def show_online(self, obj):
        return obj.online()


admin.site.site_header = "Display Screen Admin"
