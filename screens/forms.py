from screens.models import Playlist
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, FileInput, FileField


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


class SourceBulkCreateForm(PlaylistAssigningSourceForm):
    files = MultiFileField(help_text="Only upload one type of file at a time resolution of files should be 1360x768, videos must be mp4")

    def is_valid(self):
        """Return True if the form has no errors, or False otherwise."""
        self.instance.bulk_create = True
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
