from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.TextChoices):
    AUTO = "auto", _("Auto")
    LIGHT = "light", _("Light")
    DARK = "dark", _("Dark")


class UserPreferences(models.Model):
    """
    Settings every user chooses for themselves, independent of the project. Users only get preferences once they
    change one of them, until then the defaults apply.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="ui_preferences",
    )
    theme = models.CharField(
        _("Theme"),
        max_length=5,
        choices=Theme.choices,
        default=Theme.AUTO,
        help_text=_("Auto follows the light or dark mode of the device"),
    )

    class Meta:
        verbose_name = _("User preferences")
        verbose_name_plural = _("User preferences")

    def __str__(self) -> str:
        return str(self.user)
