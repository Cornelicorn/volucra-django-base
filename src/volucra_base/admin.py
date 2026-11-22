from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import UserPreferences
from .preferences import registry


class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ("user", "values")

    def clean_values(self):
        values = self.cleaned_data["values"]
        if not isinstance(values, dict):
            raise ValidationError(_("The values have to be a JSON object."))
        errors = []
        cleaned = {}
        for key, value in values.items():
            if key not in registry:
                errors.append(_("{key}: There is no such preference.").format(key=key))
                continue
            try:
                cleaned[key] = registry[key].clean(value)
            except ValidationError as error:
                errors.append(f"{key}: {' '.join(error.messages)}")
        if errors:
            raise ValidationError(errors)
        return cleaned


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    form = UserPreferencesForm
    list_display = ("user",)
    search_fields = ("user__username",)
