from django.conf import settings

DEFAULTS = {
    # Shown as the page title and as the brand of the navbar
    "SITE_NAME": "Django",
    # Key of the localStorage entry the theme of the browser is kept in
    "THEME_STORAGE_KEY": "tabler_ui_theme",
}


def get_setting(name: str):
    """Returns the setting TABLER_UI_<name> or its default"""
    return getattr(settings, f"TABLER_UI_{name}", DEFAULTS[name])
