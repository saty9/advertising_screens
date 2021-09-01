from admin_ordering.admin import OrderableAdmin
from django.conf.urls import url
from django.contrib import admin

# Register your models here.
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, FileInput, FileField, ClearableFileInput
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


class MultiFileInput(FileInput):
    def __init__(self, attrs=None):
        if attrs is not None:
            attrs = attrs.copy()
        else:
            attrs = {}
        attrs["multiple"] = True
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)


class MultiFileField(FileField):
    widget = MultiFileInput

    def to_python(self, data):
        if data in self.empty_values:
            return None

        for file in data:
            # UploadedFile objects should have name and size attributes.
            try:
                file_name = file.name
                file_size = file.size
            except AttributeError:
                raise ValidationError(self.error_messages['invalid'], code='invalid')

            if self.max_length is not None and len(file_name) > self.max_length:
                params = {'max': self.max_length, 'length': len(file_name)}
                raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)
            if not file_name:
                raise ValidationError(self.error_messages['invalid'], code='invalid')
            if not self.allow_empty_file and not file_size:
                raise ValidationError(self.error_messages['empty'], code='empty')

        return data

    def clean(self, data, initial=None):
        # If the widget got contradictory inputs, we raise a validation error
        if data is object():
            raise ValidationError(self.error_messages['contradiction'], code='contradiction')
        # False means the field value should be cleared; further validation is
        # not needed.
        if data is False:
            if not self.required:
                return False
            # If the field is required, clearing is not possible (the widget
            # shouldn't return False data in that case anyway). False is not
            # in self.empty_value; if a False value makes it this far
            # it should be validated from here on out as None (so it will be
            # caught by the required check).
            data = None
        if not data and initial:
            return initial
        return super().clean(data)

    def bound_data(self, data, initial):
        if data in (None, object()):
            return initial
        return data


class SourceBulkCreateForm(PlaylistAssigningSourceForm):
    files = MultiFileField(help_text="Only upload one type of file at a time resolution of files should be 1360x768, videos must be mp4")

    def is_valid(self):
        """Return True if the form has no errors, or False otherwise."""
        return self.is_bound and not self.errors

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            for file in self.cleaned_data["files"]:
                self.instance.file = file
                self.instance.id = None
                self.instance.name = file.name
                self.instance.save()
                self.instance.playlists.set(self.cleaned_data["playlists"], through_defaults={"number": 10})
                self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance


class SourceDisplay(admin.ModelAdmin):
    readonly_fields = ('image_preview',)
    list_display = ('name', 'playlist_names', 'created_at')


    def get_urls(self):
        urls = super(SourceDisplay, self).get_urls()
        my_urls = [
            url(r'^bulk_create/$', self.bulk_create_view),
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
