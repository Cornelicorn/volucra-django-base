from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserPreferences(models.Model):
    """
    The preferences of one user, of all apps. values only contains the preferences the user chose, by key
    "<app label>.<name>", the declared defaults apply to the others. Use volucra_base.preferences.get_preferences()
    to read and change them.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    values = models.JSONField(
        _("Values"),
        default=dict,
        blank=True,
        encoder=DjangoJSONEncoder,
        help_text=_('The preferences the user chose, by key, e.g. {"tabler_ui.theme": "dark"}. Others have their default.'),
    )

    class Meta:
        verbose_name = _("User preferences")
        verbose_name_plural = _("User preferences")

    def __str__(self) -> str:
        return str(self.user)
