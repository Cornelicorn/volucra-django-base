from pathlib import Path

SECRET_KEY = "only-for-the-tests"
DEBUG = False
ALLOWED_HOSTS = ["testserver"]

INSTALLED_APPS = [
    # Before tabler_ui and django.contrib.admin, so its login pages with the SSO button are used
    "volucra_base",
    "tabler_ui",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "django_tables2",
    "crispy_forms",
    "crispy_bootstrap5",
    "social_django",
    "tests.prefapp",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(__file__).resolve().parent / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "volucra_base.context_processors.sso",
            ],
        },
    },
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
STATIC_URL = "/static/"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

AUTHENTICATION_BACKENDS = (
    "social_core.backends.open_id_connect.OpenIdConnectAuth",
    "django.contrib.auth.backends.ModelBackend",
)
SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_OIDC_OIDC_ENDPOINT = ""

TABLER_UI_SITE_NAME = "Test Site"

from tabler_ui import defaults as tabler_ui_defaults

CRISPY_ALLOWED_TEMPLATE_PACKS = tabler_ui_defaults.CRISPY_ALLOWED_TEMPLATE_PACKS
CRISPY_TEMPLATE_PACK = tabler_ui_defaults.CRISPY_TEMPLATE_PACK
DJANGO_TABLES2_TEMPLATE = tabler_ui_defaults.DJANGO_TABLES2_TEMPLATE
DJANGO_TABLES2_TABLE_ATTRS = tabler_ui_defaults.DJANGO_TABLES2_TABLE_ATTRS
