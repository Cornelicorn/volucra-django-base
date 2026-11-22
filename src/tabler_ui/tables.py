import django_tables2 as tables
from django.utils.translation import gettext_lazy as _


class ButtonColumn(tables.TemplateColumn):
    """
    A narrow, right aligned column with a button in every row. The template gets the URL name the button links to as
    url_target.
    """

    def __init__(self, template_name: str, url_target: str, verbose_name: str):
        super().__init__(
            template_name=template_name,
            verbose_name=verbose_name,
            attrs={
                "td": {"align": "right"},
                "th": {"style": "text-align: right;", "class": "w-1"},
            },
            orderable=False,
        )
        self.extra_context.update({"url_target": url_target})


class OpenColumn(ButtonColumn):
    """Links to url_target with the id of the record, e.g. its detail page"""

    def __init__(self, url_target: str, verbose_name: str = _("Open")):
        super().__init__("tabler_ui/tables/columns/open.html", url_target, verbose_name)


class EditColumn(ButtonColumn):
    """Links to url_target with the id of the record, e.g. its edit page"""

    def __init__(self, url_target: str, verbose_name: str = _("Edit")):
        super().__init__("tabler_ui/tables/columns/edit.html", url_target, verbose_name)


class DeleteColumn(ButtonColumn):
    """Links to url_target with the id of the record, e.g. its delete page"""

    def __init__(self, url_target: str, verbose_name: str = _("Delete")):
        super().__init__("tabler_ui/tables/columns/delete.html", url_target, verbose_name)


class HumanizedSecondsColumn(tables.TemplateColumn):
    """Shows a number of seconds like "1 hour 2 minutes" """

    def __init__(self, **kwargs):
        super().__init__(template_name="tabler_ui/tables/columns/humanized_seconds.html", **kwargs)
