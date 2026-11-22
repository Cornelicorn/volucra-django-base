"""
Recommended values of settings of other apps, so they match the templates of tabler_ui. Use them in the settings of
the project, e.g.

    from tabler_ui import defaults as tabler_ui_defaults

    DJANGO_TABLES2_TABLE_ATTRS = tabler_ui_defaults.DJANGO_TABLES2_TABLE_ATTRS
"""

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5-responsive.html"

DJANGO_TABLES2_TABLE_ATTRS = {
    "class": "table table-responsive table-striped",
    "td": {
        "class": "align-middle",
    },
    "th": {
        "_ordering": {
            "ascending": "ti ti-sort-ascending",
            "descending": "ti ti-sort-descending",
        },
    },
}
