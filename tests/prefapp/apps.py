from typing import ClassVar

from django import forms
from django.apps import AppConfig


class PrefAppConfig(AppConfig):
    """An app which declares preferences of its own next to the theme of tabler_ui"""

    name = "tests.prefapp"
    label = "prefapp"
    user_preferences: ClassVar[dict[str, forms.Field]] = {
        "notifications": forms.BooleanField(required=False, initial=True),
        "page_size": forms.IntegerField(min_value=5, max_value=100, initial=25),
    }
