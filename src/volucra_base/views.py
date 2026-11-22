from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django_tables2 import MultiTableMixin

from .preferences import get_preferences


class InitialCreateView(CreateView):
    """Fills the form with the values of the query string, e.g. ?game=1 preselects the game"""

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.GET.items())
        return initial


class FilteredMultiTableMixin(MultiTableMixin):
    """
    Provides the filters of the tables to the template as filters, get_tables_data() has to store them in
    self.filters in the order of the tables. The columns of fields left out of an ExcludeFilterSet with exclude are
    hidden as well, as they have the same value in every row.
    """

    def get_tables(self):
        tables = super().get_tables()
        for table, filterset in zip(tables, self.filters):
            table.exclude = (*table.exclude, *getattr(filterset, "excluded", ()))
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filters": self.filters})
        return context


@require_POST
def save_preferences(request):
    """
    Saves the preferences posted as form data (key=value) for the logged in user, e.g. the theme of the theme
    switcher of tabler_ui. Answers with 204 or with the errors by key as JSON.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"errors": {"__all__": [_("Log in to save preferences.")]}}, status=403)
    values = {key: value for key, value in request.POST.items() if key != "csrfmiddlewaretoken"}
    if not values:
        return JsonResponse({"errors": {"__all__": [_("No preferences were given.")]}}, status=400)
    try:
        get_preferences(request.user).update(values)
    except ValidationError as error:
        return JsonResponse({"errors": error.message_dict}, status=400)
    return HttpResponse(status=204)
