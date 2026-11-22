"""Views which use the generic templates with the models of django.contrib.auth"""

import django_tables2 as tables
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import Group, User
from django.views.generic import DeleteView, DetailView, UpdateView
from django_filters import CharFilter
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from tabler_ui.forms import FilterForm
from tabler_ui.tables import DeleteColumn, EditColumn, HumanizedSecondsColumn, OpenColumn
from volucra_base.filters import ExcludeFilterSet
from volucra_base.views import FilteredMultiTableMixin, InitialCreateView


class GroupTable(tables.Table):
    open = OpenColumn("group-detail")
    edit = EditColumn("group-edit")
    delete = DeleteColumn("group-delete")

    class Meta:
        model = Group
        fields = ("name",)


class UserTable(tables.Table):
    seconds = HumanizedSecondsColumn(accessor="id", verbose_name="Seconds")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "is_active",
        )


class GroupFilter(ExcludeFilterSet):
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Group
        form = FilterForm
        fields = ("name",)


class UserFilter(ExcludeFilterSet):
    class Meta:
        model = User
        form = FilterForm
        fields = (
            "username",
            "first_name",
            "is_active",
        )


class GroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.title = "Group"
        self.helper.add_input(Submit("save", "Save"))

    class Meta:
        model = Group
        fields = ("name",)


class GroupListView(SingleTableMixin, FilterView):
    model = Group
    table_class = GroupTable
    filterset_class = GroupFilter
    template_name = "tabler_ui/generic/object_list.html"


class GroupCreateView(InitialCreateView):
    model = Group
    form_class = GroupForm
    template_name = "tabler_ui/generic/object_create.html"
    success_url = "/groups/"


class GroupEditView(UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "tabler_ui/generic/object_edit.html"
    success_url = "/groups/"


class GroupDeleteView(DeleteView):
    model = Group
    template_name = "tabler_ui/generic/object_confirm_delete.html"
    success_url = "/groups/"


class GroupDetailView(FilteredMultiTableMixin, DetailView):
    model = Group
    tables = (UserTable,)
    template_name = "group_detail.html"

    def get_tables_data(self):
        users = UserFilter(self.request.GET, User.objects.filter(groups=self.object), prefix="users", exclude=["is_active"])
        self.filters = [users]
        return [users.qs]
