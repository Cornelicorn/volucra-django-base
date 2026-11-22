"""
Preferences of tabler_ui, e.g. the theme, are declared in TablerUIConfig.user_preferences. tabler_ui doesn't store
them itself: an installed app can provide a preference store by naming it in the attribute user_preference_store of
its AppConfig (a dotted path or the object itself), as volucra_base does. Without one, the theme is only kept in the
browser.

A preference store provides:

    get_chosen(request, key)
        The value the user of the request chose for the preference key, e.g. "tabler_ui.theme", or None if they
        haven't chosen one or can't save preferences.

    get_save_url(request)
        The URL the user of the request can POST preferences to as form data (key=value), or None if they can't save
        preferences, e.g. because they aren't logged in.
"""

from django.apps import apps
from django.utils.module_loading import import_string

THEME_KEY = "tabler_ui.theme"


def get_preference_store():
    """Returns the preference store of the first installed app which provides one, or None"""
    for config in apps.get_app_configs():
        store = getattr(config, "user_preference_store", None)
        if store:
            return import_string(store) if isinstance(store, str) else store
    return None


def get_theme_preference(request) -> dict:
    """The theme the user of the request saved and where they can save it, if an installed app stores preferences"""
    store = get_preference_store()
    if request is None or store is None:
        return {"key": THEME_KEY, "saved": None, "save_url": None}
    return {"key": THEME_KEY, "saved": store.get_chosen(request, THEME_KEY), "save_url": store.get_save_url(request)}
