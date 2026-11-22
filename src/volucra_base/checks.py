from django.apps import apps
from django.core import checks

# Apps whose templates volucra_base extends with the login with OpenID Connect
EXTENDED_APPS = {
    "tabler_ui": "login page",
    "django.contrib.admin": "admin login page",
}


@checks.register()
def check_app_order(app_configs, **kwargs):
    """Templates of apps earlier in INSTALLED_APPS take precedence, so volucra_base has to come first"""
    names = [config.name for config in apps.get_app_configs()]
    position = names.index("volucra_base")
    return [
        checks.Warning(
            f"volucra_base comes after {name} in INSTALLED_APPS, so the {page} doesn't offer the login with OpenID Connect.",
            hint=f"Move volucra_base before {name} in INSTALLED_APPS.",
            obj="volucra_base",
            id="volucra_base.W001",
        )
        for name, page in EXTENDED_APPS.items()
        if name in names and names.index(name) < position
    ]
