# Volucra Django base

Reusable building blocks for Django projects, split into two apps:

- **`tabler_ui`**: the look of a project, based on [Tabler](https://tabler.io)
  - base layout, navbar and error pages (400, 403, 404, 500)
  - generic pages to list, show, create, edit and delete objects
  - [django-tables2](https://django-tables2.readthedocs.io) and
    [django-filter](https://django-filter.readthedocs.io) templates: table cards, empty tables, filter button and
    modal, the `FilterForm` for filtersets, and `OpenColumn`, `EditColumn`, `DeleteColumn` and
    `HumanizedSecondsColumn`
  - login, logout, password change and password reset pages
  - light, dark and auto theme with a switcher in the navbar, kept in the browser
  - no models or migrations
- **`volucra_base`**: user preferences, views and the login with OpenID Connect
  - `UserPreferences`: one row per user with the preferences all installed apps declare, e.g. the theme of
    `tabler_ui`, which then follows the user across devices
  - login with OpenID Connect through [social-auth-app-django](https://python-social-auth.readthedocs.io), with a
    pipeline step that maps OIDC groups to Django groups, and an SSO button which it adds to the login pages of
    `tabler_ui` and the admin
  - `InitialCreateView`, `FilteredMultiTableMixin` and `ExcludeFilterSet`

Both apps can be used on their own. If both are installed and in `INSTALLED_APPS`, `volucra_base` adds the SSO
button to the login page of `tabler_ui` and saves its theme in the user preferences.

## Installation

It needs Python 3.12 or newer and Django 6.1. Install it from PyPI:

```sh
uv add volucra-django-base
```

Add the extra `sso` (`volucra-django-base[sso]`) to get social-auth-app-django for the login with OpenID Connect.

## Setup

`settings.py`:

```python
INSTALLED_APPS = [
    # volucra_base has to come before tabler_ui and django.contrib.admin, so their login pages show the SSO button
    "volucra_base",
    "tabler_ui",
    "django.contrib.admin",
    # ...
    "django_filters",
    "django_tables2",
    "crispy_forms",
    "crispy_bootstrap5",
]

TEMPLATES = [
    {
        # ...
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",  # required by tabler_ui
                "django.contrib.auth.context_processors.auth",
                # ...
                "volucra_base.context_processors.sso",
            ],
        },
    },
]

from tabler_ui import defaults as tabler_ui_defaults

CRISPY_ALLOWED_TEMPLATE_PACKS = tabler_ui_defaults.CRISPY_ALLOWED_TEMPLATE_PACKS
CRISPY_TEMPLATE_PACK = tabler_ui_defaults.CRISPY_TEMPLATE_PACK
DJANGO_TABLES2_TEMPLATE = tabler_ui_defaults.DJANGO_TABLES2_TEMPLATE
DJANGO_TABLES2_TABLE_ATTRS = tabler_ui_defaults.DJANGO_TABLES2_TABLE_ATTRS

TABLER_UI_SITE_NAME = "My Project"
```

`urls.py`:

```python
urlpatterns = [
    path("accounts/", include("tabler_ui.account_urls")),  # without a namespace
    path("", include("volucra_base.urls")),  # saving user preferences, at preferences/
    # ...
]
```

Then run `python manage.py migrate` to create the table of the user preferences.

### Settings

| Setting                          | Default             | Description                                                              |
| -------------------------------- | ------------------- | ------------------------------------------------------------------------ |
| `TABLER_UI_SITE_NAME`            | `"Django"`          | Page title and brand of the navbar                                       |
| `TABLER_UI_THEME_STORAGE_KEY`    | `"tabler_ui_theme"` | localStorage key the browser keeps the theme in                          |
| `VOLUCRA_SSO_LABEL`              | `"Volucra SSO"`     | Label of the SSO button on the login pages                               |
| `SOCIAL_AUTH_OIDC_OIDC_ENDPOINT` | unset               | The SSO button is shown once this is set                                 |
| `ADMIN_GROUP`                    | `None`              | OIDC group whose members become staff and superusers, `None` to not sync |

### Login with OpenID Connect

Configure social-auth-app-django as usual and add the pipeline step:

```python
SOCIAL_AUTH_PIPELINE = (
    # ... the default steps of social-auth-app-django
    "volucra_base.auth_pipeline.oidc.assign_groups_and_attributes",
)
```

volucra_base adds the SSO button by extending `tabler_ui/registration/login.html` (block `login_footer`) and
`admin/login.html`. Templates of apps earlier in `INSTALLED_APPS` take precedence, so this only works while
volucra_base comes before `tabler_ui` and `django.contrib.admin`. The system check `volucra_base.W001` warns
otherwise.

## Usage

### Templates

Pages extend `tabler_ui/layout.html` (with navbar) or `tabler_ui/base.html` (empty page) and fill the block
`content` or `body`. Further blocks of `base.html` are `title`, `stylesheets`, `head` and `scripts`.

The generic templates are meant to be used as `template_name` of the generic views or to be extended:

| Template                                          | Blocks                                                                                           |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `tabler_ui/generic/object_list.html`              | `page-pretitle`, `page-title`, `extra_button`, `createbutton`, `alerts`, `table`                 |
| `tabler_ui/generic/object_detail.html`            | `page-pretitle`, `page-title`, `object_buttons`, `alerts`, `specific_content`                    |
| `tabler_ui/generic/object_create.html`/`_edit`    | as `object_detail.html`, shows `form` with crispy forms and `form.helper.title` as title          |
| `tabler_ui/generic/object_confirm_delete.html`    | as `object_detail.html`                                                                          |
| `tabler_ui/tables/table_card.html`/`table_inline` | include them `with table=... filter=... id_filter_modal=...`, optionally `table_heading`         |

### Customizing the navbar and the base layout

Override `tabler_ui/navbar.html` in the templates directory of the project with a template that extends it, e.g.
`templates/tabler_ui/navbar.html`:

```django
{% extends "tabler_ui/navbar.html" %}
{% load i18n tabler_ui %}

{% block navbar_menu %}
    {% url "app:item-list" as items_url %}
    <li class="nav-item {% if request.path|startswith:items_url %}active{% endif %}">
        <a href="{{ items_url }}" class="nav-link">{% trans "Items" %}</a>
    </li>
{% endblock navbar_menu %}
```

The navbar has the blocks `navbar_brand`, `navbar_menu`, `account_menu` and `account_menu_items`. The same way, an
override of `tabler_ui/base.html` can add the stylesheets of the project to every page:

```django
{% extends "tabler_ui/base.html" %}
{% load static %}

{% block stylesheets %}
    {{ block.super }}
    <link href="{% static "css/project.css" %}" rel="stylesheet" />
{% endblock stylesheets %}
```

### Theme

The theme switcher keeps the theme in the localStorage of the browser. If `volucra_base` is installed and in
`INSTALLED_APPS`, it saves it in the user preferences of logged in users as well. When a user logs in on a new device,
the saved theme replaces the one of the device. Users who haven't saved one yet keep the theme the device used so far.

### User preferences

Any app can declare preferences in the attribute `user_preferences` of its `AppConfig`, as a dictionary of form fields.
`volucra_base` collects them on startup and keeps the values each user chooses in one `UserPreferences` per user. The
key of a preference is `<app label>.<name>`, its default is the `initial` value of its field:

```python
class ShopConfig(AppConfig):
    name = "shop"
    user_preferences: ClassVar[dict[str, forms.Field]] = {
        "newsletter": forms.BooleanField(label=_("Newsletter"), required=False, initial=False),
    }
```

An app which needs its models for the fields, e.g. for a `ModelChoiceField`, returns the dictionary from the method
`get_user_preferences()` of its `AppConfig` instead, which is only called once the models are loaded.

```python
from volucra_base.preferences import get_preferences

preferences = get_preferences(request.user)
preferences["shop.newsletter"]  # the value the user chose or the default
preferences.get_chosen("shop.newsletter")  # None if the user hasn't chosen one
preferences.update({"shop.newsletter": True})  # validated with the form fields, raises a ValidationError otherwise
```

The view `volucra_base:save-preferences` (`preferences/`) saves the preferences posted as form data (`key=value`) for
the logged in user, as the theme switcher does. It answers with 204, or with the errors by key as JSON. Values stored
for preferences which are no longer declared, or which are no longer valid, are ignored.

`volucra_base.preferences.get_save_url()` returns the URL of the view, or `None` if the project didn't include
`volucra_base.urls`. Without volucra_base or its URLs, `tabler_ui` keeps the theme in the browser only.

## Development

```sh
uv sync
uv run python -m django test --settings=tests.settings --pythonpath=.
uv run ruff check && uv run ruff format --check
uv run djlint --check src && uv run djhtml --check src
uv run mypy
```

### Releases

Set the new version in `pyproject.toml`, commit it and push a tag with the same version, e.g. `v0.2.0`. The release
workflow then builds the package and drafts a GitHub release with the wheel, the source distribution and generated
release notes, which only has to be published. It fails if the tag doesn't match the version in `pyproject.toml`.

Publishing the release starts the publish workflow, which uploads the wheel and the source distribution of the release
to PyPI with [Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no API token is stored in the
repository. It runs in the GitHub environment `pypi`, which can require an approval before the upload.

### Dependency updates

Dependabot updates `uv.lock` and the GitHub Actions weekly. The lower bound of each dependency is the oldest version
it was tested with, the upper bound the next version which may break it according to the versioning of that project:

- Django and django-stubs: the next feature release, which may contain backwards incompatible changes and remove
  deprecated features
- crispy-bootstrap5: the next release, it uses calendar versions without a compatibility promise
- django-filter: the next year, it only removes deprecated features in the first release of a year
- mypy and ruff: the next minor version, which may report new errors
- the others: the next major version

When a new version beyond the upper bound comes out, Dependabot raises it in its pull request
(`versioning-strategy: increase-if-necessary`), so these updates are visible in `pyproject.toml`. Versions within the
bounds only update `uv.lock`, the lower bounds stay.
