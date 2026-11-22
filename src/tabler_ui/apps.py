from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TablerUIConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tabler_ui"
    verbose_name = _("Tabler UI")
