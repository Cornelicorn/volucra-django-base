from django import template

from ..conf import get_setting
from ..models import UserPreferences

register = template.Library()


@register.simple_tag
def tabler_ui_setting(name):
    """Returns the setting TABLER_UI_<name> or its default, e.g. {% tabler_ui_setting "SITE_NAME" %}"""
    return get_setting(name)


@register.simple_tag(takes_context=True)
def tabler_ui_theme(context):
    """Returns the theme saved in the preferences of the logged in user, or None if they haven't chosen one yet"""
    request = context.get("request")
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return None
    return UserPreferences.objects.filter(user=user).values_list("theme", flat=True).first()


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
