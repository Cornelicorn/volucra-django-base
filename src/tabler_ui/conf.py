from typing import Any

from django.conf import settings

DEFAULTS = {
    # Shown as the page title and as the brand of the navbar
    "SITE_NAME": "Django",
    # Key of the localStorage entry the theme of the browser is kept in
    "THEME_STORAGE_KEY": "tabler_ui_theme",
    # Settings of tabler-themes.css, None for the default of Tabler. The gray scale is the one of Tabler up to 1.5 with a
    # blue tint, Tabler 1.6 changed its default to "neutral".
    "THEME_BASE": "gray",
    "THEME_PRIMARY": None,
    "THEME_RADIUS": None,
    "THEME_FONT": None,
}


def get_setting(name: str) -> Any:
    """Returns the setting TABLER_UI_<name> or its default"""
    return getattr(settings, f"TABLER_UI_{name}", DEFAULTS[name])
