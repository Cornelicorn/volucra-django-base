from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VolucraBaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "volucra_base"
    verbose_name = _("Volucra base")

    def ready(self):
        from . import checks  # noqa: F401
