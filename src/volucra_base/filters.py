from django_filters import FilterSet


class ExcludeFilterSet(FilterSet):
    """
    Leaves out the filters of the fields given in exclude, which have the same value for all objects, e.g. the game
    of the submissions of a game. FilteredMultiTableMixin also hides their columns.
    """

    def __init__(self, *args, exclude=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.excluded = tuple(exclude)
        for name in self.excluded:
            del self.filters[name]
