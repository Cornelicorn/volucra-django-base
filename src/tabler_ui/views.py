from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from .models import Theme, UserPreferences


@require_POST
def set_theme(request):
    """
    Saves the theme chosen with the theme switcher of the navbar in the preferences of the user. Anonymous users
    only keep it in the localStorage of their browser, so nothing is saved for them.
    """
    theme = request.POST.get("theme")
    if theme not in Theme.values:
        return HttpResponseBadRequest()
    if request.user.is_authenticated:
        UserPreferences.objects.update_or_create(user=request.user, defaults={"theme": theme})
    return HttpResponse(status=204)
