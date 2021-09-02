from admin_ordering.admin import OrderableAdmin
from django.contrib import admin

# Register your models here.
from django import forms
from django.forms import ModelForm

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


class PlaylistAssigningSourceForm(ModelForm):
    playlists = forms.ModelMultipleChoiceField(label="Playlists", queryset=Playlist.objects.all(), widget=forms.CheckboxSelectMultiple)

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        if commit:
            self.instance.save()
            # If committing, save the instance and the m2m data immediately.
            self.instance.playlists.set(self.cleaned_data["playlists"], through_defaults={"number": 10})
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance


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

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = PlaylistAssigningSourceForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
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
