from django.views.generic import CreateView
from django_tables2 import MultiTableMixin


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
