from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VolucraBaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "volucra_base"
    verbose_name = _("Volucra base")

    # Saves the preferences tabler_ui declares, e.g. the theme, see tabler_ui.preferences
    user_preference_store = "volucra_base.preferences.store"

    def ready(self):
        from . import checks  # noqa: F401
        from .preferences import registry

        # Report invalid preference declarations on startup instead of on first use
        registry.load()
