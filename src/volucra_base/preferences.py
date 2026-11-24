"""
User preferences which any installed app can declare, saved in one UserPreferences per user.

Apps declare their preferences as a dictionary of form fields in the attribute user_preferences of their AppConfig,
or return it from its method get_user_preferences() if they need their models for it. The key of a preference is
"<app label>.<name>", its default is the initial value of its field:

    class ShopConfig(AppConfig):
        name = "shop"
        user_preferences = {
            "newsletter": forms.BooleanField(label=_("Newsletter"), required=False, initial=False),
        }

    preferences = get_preferences(request.user)
    preferences["shop.newsletter"]
    preferences.update({"shop.newsletter": True})
"""

from collections.abc import Iterator, Mapping
from types import MappingProxyType
from typing import Any

from django import forms
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.signals import setting_changed
from django.db import transaction
from django.dispatch import receiver
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

from .models import UserPreferences


class PreferenceRegistry(Mapping):
    """The form fields of the preferences the installed apps declare, by key. Collected once on first use."""

    def __init__(self):
        self._fields: Mapping[str, forms.Field] | None = None

    def load(self) -> Mapping[str, forms.Field]:
        if self._fields is None:
            self._fields = self.collect(apps.get_app_configs())
        return self._fields

    def clear(self):
        self._fields = None

    @staticmethod
    def collect(app_configs) -> Mapping[str, forms.Field]:
        fields = {}
        for config in app_configs:
            get_declared = getattr(config, "get_user_preferences", None)
            declared = get_declared() if callable(get_declared) else getattr(config, "user_preferences", None)
            for name, field in (declared or {}).items():
                key = f"{config.label}.{name}"
                if not isinstance(field, forms.Field):
                    raise ImproperlyConfigured(f"The preference {key} has to be a form field, not {field!r}.")
                default = get_default(field)
                if default is not None:
                    try:
                        field.clean(default)
                    except ValidationError as error:
                        raise ImproperlyConfigured(
                            f"The default {default!r} of the preference {key} is invalid: {' '.join(error.messages)}"
                        ) from error
                fields[key] = field
        return MappingProxyType(fields)

    def __getitem__(self, key: str) -> forms.Field:
        return self.load()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.load())

    def __len__(self) -> int:
        return len(self.load())


registry = PreferenceRegistry()


@receiver(setting_changed)
def clear_registry(*, setting, **kwargs):
    # Tests can change the installed apps
    if setting == "INSTALLED_APPS":
        registry.clear()


def get_default(field: forms.Field) -> Any:
    return field.initial() if callable(field.initial) else field.initial


class Preferences:
    """
    The preferences of one user. Reading a preference returns the value the user chose or its default, the values
    of anonymous users are always the defaults and can't be changed.

    The row of the user is read through user.preferences, which Django caches on the user object, also if there is
    none, so the preferences are loaded once per user object, e.g. once per request for request.user.
    """

    def __init__(self, user):
        self.user = user

    @property
    def _values(self) -> dict[str, Any]:
        if not self.user.is_authenticated:
            return {}
        try:
            return self.user.preferences.values
        except UserPreferences.DoesNotExist:
            return {}

    def get_chosen(self, key: str) -> Any:
        """The value the user chose for the preference, None if they haven't chosen a valid one"""
        field = registry[key]
        if key not in self._values:
            return None
        try:
            return field.clean(self._values[key])
        except ValidationError:
            # The declaration changed since the value was saved
            return None

    def __getitem__(self, key: str) -> Any:
        value = self.get_chosen(key)
        return get_default(registry[key]) if value is None else value

    def update(self, values: Mapping[str, Any]):
        """Validates and saves the given preferences, raises a ValidationError with the errors by key otherwise"""
        if not self.user.is_authenticated:
            raise ValueError("The preferences of anonymous users can't be saved.")
        errors = {}
        cleaned = {}
        for key, value in values.items():
            if key not in registry:
                errors[key] = [_("There is no such preference.")]
                continue
            try:
                cleaned[key] = registry[key].clean(value)
            except ValidationError as error:
                errors[key] = error.messages
        if errors:
            raise ValidationError(errors)

        # Lock the row, so concurrent changes of other preferences aren't lost
        with transaction.atomic():
            instance, _created = UserPreferences.objects.select_for_update().get_or_create(user=self.user)
            instance.values.update(cleaned)
            instance.save(update_fields=["values"])
        # A row which already existed isn't the one cached on the user object, so replace that
        self.user.preferences = instance


def get_preferences(user) -> Preferences:
    """The preferences of the user, see Preferences"""
    return Preferences(user)


def get_save_url() -> str | None:
    """
    The URL logged in users can POST their preferences to as form data (key=value), None if the project didn't
    include volucra_base.urls
    """
    try:
        return reverse("volucra_base:save-preferences")
    except NoReverseMatch:
        return None
