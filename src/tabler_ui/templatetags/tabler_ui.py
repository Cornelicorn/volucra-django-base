from django import template
from django.apps import apps
from django.utils.html import format_html_join

from ..conf import get_setting

register = template.Library()

THEME_KEY = "tabler_ui.theme"

# The attributes of tabler-themes.css and the settings they come from
THEME_ATTRIBUTES = {
    "data-bs-theme-base": "THEME_BASE",
    "data-bs-theme-primary": "THEME_PRIMARY",
    "data-bs-theme-radius": "THEME_RADIUS",
    "data-bs-theme-font": "THEME_FONT",
}


@register.simple_tag
def tabler_ui_setting(name):
    """Returns the setting TABLER_UI_<name> or its default, e.g. {% tabler_ui_setting "SITE_NAME" %}"""
    return get_setting(name)


@register.simple_tag
def tabler_ui_theme_attributes():
    """
    Returns the attributes of tabler-themes.css for the settings TABLER_UI_THEME_BASE, _PRIMARY, _RADIUS and _FONT,
    leaving out those which are None, e.g. <html{% tabler_ui_theme_attributes %}>
    """
    values = ((attribute, get_setting(name)) for attribute, name in THEME_ATTRIBUTES.items())
    return format_html_join("", ' {}="{}"', ((attribute, value) for attribute, value in values if value is not None))


@register.simple_tag(takes_context=True)
def tabler_ui_theme_preference(context):
    """
    Returns the theme the logged in user saved (saved, None if they haven't saved one), where they can save it
    (save_url, None if they can't) and under which key (key). If volucra_base is installed and enabled, the theme is
    saved in the preferences of the user, otherwise both are None and the theme is only kept in the browser.
    """
    theme = {"key": THEME_KEY, "saved": None, "save_url": None}
    user = getattr(context.get("request"), "user", None)
    # is_installed() is False if volucra_base isn't installed or isn't in INSTALLED_APPS. It's checked instead of catching
    # an ImportError, as volucra_base can be imported while it isn't in INSTALLED_APPS, its models then raise a
    # RuntimeError.
    if user is not None and user.is_authenticated and apps.is_installed("volucra_base"):
        from volucra_base.preferences import get_preferences, get_save_url

        save_url = get_save_url()
        # If the project didn't include the URLs of volucra_base, the theme is only kept in the browser, so the theme
        # switcher can change it
        if save_url is not None:
            theme.update(saved=get_preferences(user).get_chosen(THEME_KEY), save_url=save_url)
    return theme


@register.filter
def startswith(value, prefix):
    """E.g. to highlight the navbar entry of the section of the current page: request.path|startswith:section_url"""
    return str(value).startswith(str(prefix))


@register.filter
def humanize_seconds(time):
    """Shows a number of seconds like "1 week 2 days 3 hours 4 minutes 5 seconds", leaving out zero units"""
    seconds = time
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    weeks = days // 7

    seconds = seconds % 60
    minutes = minutes % 60
    hours = hours % 24
    days = days % 7

    t_seconds = f"{seconds} second" if seconds else ""
    t_minutes = f"{minutes} minute" if minutes else ""
    t_hours = f"{hours} hour" if hours else ""
    t_days = f"{days} day" if days else ""
    t_weeks = f"{weeks} week" if weeks else ""

    t_seconds = f"{t_seconds}s" if seconds > 1 else t_seconds
    t_minutes = f"{t_minutes}s" if minutes > 1 else t_minutes
    t_hours = f"{t_hours}s" if hours > 1 else t_hours
    t_days = f"{t_days}s" if days > 1 else t_days
    t_weeks = f"{t_weeks}s" if weeks > 1 else t_weeks

    return " ".join(t for t in (t_weeks, t_days, t_hours, t_minutes, t_seconds) if t)
