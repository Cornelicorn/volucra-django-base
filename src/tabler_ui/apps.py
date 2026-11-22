from typing import ClassVar

from django import forms
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TablerUIConfig(AppConfig):
    name = "tabler_ui"
    verbose_name = _("Tabler UI")

    # tabler_ui keeps no data itself. An installed app with a preference store, e.g. volucra_base, saves these
    # preferences for logged in users, see tabler_ui.preferences
    user_preferences: ClassVar[dict[str, forms.Field]] = {
        "theme": forms.ChoiceField(
            label=_("Theme"),
            help_text=_("Auto follows the light or dark mode of the device"),
            choices=[("auto", _("Auto")), ("light", _("Light")), ("dark", _("Dark"))],
            initial="auto",
        ),
    }
