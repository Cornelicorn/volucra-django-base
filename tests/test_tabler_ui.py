import sys
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import connection
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from tabler_ui.templatetags.tabler_ui import humanize_seconds, startswith, tabler_ui_theme_preference
from volucra_base.models import UserPreferences


class ThemeTests(TestCase):
    """The theme with volucra_base, which saves it in the preferences of logged in users"""

    def setUp(self):
        self.user = User.objects.create_user("user", password="password")

    def test_saved_theme_is_rendered(self):
        UserPreferences.objects.create(user=self.user, values={"tabler_ui.theme": "dark"})
        self.client.force_login(self.user)
        response = self.client.get("/groups/")
        self.assertContains(response, 'data-bs-theme="dark"')
        self.assertContains(response, 'data-tabler-ui-theme="dark"')
        self.assertContains(response, 'data-tabler-ui-theme-url="/preferences/"')
        self.assertContains(response, 'data-tabler-ui-theme-key="tabler_ui.theme"')
        self.assertContains(response, "data-tabler-ui-csrf-token=")

    def test_users_without_preferences_use_the_theme_of_the_browser(self):
        self.client.force_login(self.user)
        response = self.client.get("/groups/")
        self.assertContains(response, 'data-bs-theme="light"')
        self.assertContains(response, 'data-tabler-ui-theme=""')
        self.assertContains(response, 'data-tabler-ui-theme-url="/preferences/"')

    def test_anonymous_users_dont_save_the_theme_on_the_server(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, 'data-tabler-ui-theme=""')
        self.assertNotContains(response, "data-tabler-ui-theme-url")
        self.assertNotContains(response, "data-tabler-ui-csrf-token")

    @override_settings(ROOT_URLCONF="tests.urls_without_preferences")
    def test_theme_is_only_kept_in_the_browser_without_the_urls_of_volucra_base(self):
        UserPreferences.objects.create(user=self.user, values={"tabler_ui.theme": "dark"})
        self.client.force_login(self.user)
        response = self.client.get("/groups/")
        self.assertContains(response, 'data-bs-theme="light"')
        self.assertContains(response, 'data-tabler-ui-theme=""')
        self.assertNotContains(response, "data-tabler-ui-theme-url")

    @override_settings(TABLER_UI_THEME_STORAGE_KEY="project_theme")
    def test_storage_key_is_configurable(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, 'data-tabler-ui-storage-key="project_theme"')


class ThemeWithoutVolucraBaseTests(TestCase):
    """Without volucra_base the theme is only kept in the browser"""

    def setUp(self):
        self.user = User.objects.create_user("user", password="password")
        UserPreferences.objects.create(user=self.user, values={"tabler_ui.theme": "dark"})
        self.client.force_login(self.user)
        self.installed_apps = [app for app in settings.INSTALLED_APPS if app != "volucra_base"]

    def test_theme_is_only_kept_in_the_browser_if_volucra_base_isnt_enabled(self):
        with self.settings(INSTALLED_APPS=self.installed_apps), CaptureQueriesContext(connection) as queries:
            response = self.client.get("/groups/")
        self.assertContains(response, 'data-bs-theme="light"')
        self.assertContains(response, 'data-tabler-ui-theme=""')
        self.assertNotContains(response, "data-tabler-ui-theme-url")
        self.assertNotContains(response, "data-tabler-ui-csrf-token")
        self.assertFalse([q for q in queries.captured_queries if "volucra_base" in q["sql"]])
        # The theme switcher is still there
        self.assertContains(response, 'data-tabler-ui-set-theme="dark"', count=2)

    def test_theme_is_only_kept_in_the_browser_if_volucra_base_isnt_installed(self):
        # Importing volucra_base fails, as if it weren't installed
        missing = {name: None for name in sys.modules if name.split(".")[0] == "volucra_base"}
        request = RequestFactory().get("/groups/")
        request.user = self.user
        with self.settings(INSTALLED_APPS=self.installed_apps), mock.patch.dict(sys.modules, missing):
            theme = tabler_ui_theme_preference({"request": request})
        self.assertEqual(theme, {"key": "tabler_ui.theme", "saved": None, "save_url": None})


class LayoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", password="password")
        self.staff = User.objects.create_user("staff", password="password", is_staff=True)

    def test_site_name(self):
        self.client.force_login(self.user)
        response = self.client.get("/groups/")
        self.assertInHTML("<title>Test Site</title>", response.content.decode())
        self.assertContains(response, '<a class="navbar-brand" href="/">Test Site</a>', html=True)

    def test_account_menu(self):
        self.client.force_login(self.user)
        response = self.client.get("/groups/")
        self.assertContains(response, 'href="/accounts/password_change/"')
        self.assertContains(response, 'action="/accounts/logout/"')
        self.assertNotContains(response, 'href="/admin/"')

        self.client.force_login(self.staff)
        self.assertContains(self.client.get("/groups/"), 'href="/admin/"')

    def test_theme_switchers(self):
        self.client.force_login(self.user)
        response = self.client.get("/groups/")
        # One for phones and one for larger screens
        self.assertContains(response, 'data-tabler-ui-set-theme="dark"', count=2)
        self.assertContains(response, "data-tabler-ui-theme-icon", count=2)

    def test_error_pages(self):
        for code in 400, 403, 404, 500:
            with self.subTest(code=code):
                html = render_to_string(f"{code}.html")
                self.assertIn(str(code), html)
                self.assertIn("tabler.min.css", html)

    def test_404_is_used_by_django(self):
        response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Not Found", status_code=404)
        self.assertContains(response, "tabler.min.css", status_code=404)


class GenericViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", password="password", first_name="Ada")
        self.group = Group.objects.create(name="Group A")
        self.user.groups.add(self.group)
        self.client.force_login(self.user)

    def test_list(self):
        response = self.client.get("/groups/")
        self.assertContains(response, "Group A")
        self.assertContains(response, f'href="/groups/{self.group.pk}"')
        self.assertContains(response, f'href="/groups/{self.group.pk}/edit"')
        self.assertContains(response, f'href="/groups/{self.group.pk}/delete"')
        self.assertContains(response, 'data-bs-target="#id_filter_modal"')

    def test_empty_list(self):
        response = self.client.get("/groups/", {"name": "nothing"})
        self.assertContains(response, "There is nothing to show here.")

    def test_detail_hides_columns_of_excluded_filters(self):
        response = self.client.get(f"/groups/{self.group.pk}")
        self.assertContains(response, "Ada")
        self.assertContains(response, '<h2 class="card-title">Users</h2>', html=True)
        filters = response.context["filters"]
        self.assertNotIn("is_active", filters[0].filters)
        self.assertNotIn("is_active", [column.name for column in response.context["tables"][0].columns])

    def test_create_takes_initial_values_from_the_query_string(self):
        response = self.client.get("/groups/create", {"name": "Prefilled"})
        self.assertContains(response, 'value="Prefilled"')
        self.assertContains(response, "Create")

        response = self.client.post("/groups/create", {"name": "Group B"})
        self.assertRedirects(response, "/groups/")
        self.assertTrue(Group.objects.filter(name="Group B").exists())

    def test_edit(self):
        response = self.client.get(f"/groups/{self.group.pk}/edit")
        self.assertContains(response, 'value="Group A"')

    def test_delete(self):
        response = self.client.get(f"/groups/{self.group.pk}/delete")
        self.assertContains(response, "You are about to delete")
        response = self.client.post(f"/groups/{self.group.pk}/delete")
        self.assertRedirects(response, "/groups/")
        self.assertFalse(Group.objects.exists())


class TemplateTagTests(TestCase):
    def test_humanize_seconds(self):
        self.assertEqual(humanize_seconds(1), "1 second")
        self.assertEqual(humanize_seconds(62), "1 minute 2 seconds")
        self.assertEqual(humanize_seconds(3600), "1 hour")
        self.assertEqual(humanize_seconds(7 * 24 * 3600 + 2 * 24 * 3600 + 5), "1 week 2 days 5 seconds")

    def test_startswith(self):
        self.assertTrue(startswith("/games/1", "/games/"))
        self.assertFalse(startswith("/tasks/", "/games/"))

    def test_setting(self):
        html = Template('{% load tabler_ui %}{% tabler_ui_setting "SITE_NAME" %}').render(Context())
        self.assertEqual(html, "Test Site")


class AccountPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", password="password", email="user@example.com")

    def test_login(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, 'id="id_loginForm"')
        self.assertContains(response, 'href="/accounts/password_reset/"')

        response = self.client.post("/accounts/login/", {"username": "user", "password": "password"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_login_asks_for_login_or_other_account(self):
        response = self.client.get("/accounts/login/", {"next": "/groups/"})
        self.assertContains(response, "Please login to see this page.")

        self.client.force_login(self.user)
        response = self.client.get("/accounts/login/", {"next": "/groups/"})
        self.assertContains(response, "Insufficient permissions.")

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.post("/accounts/logout/")
        self.assertContains(response, "You have been logged out")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_change(self):
        self.client.force_login(self.user)
        response = self.client.get("/accounts/password_change/")
        self.assertContains(response, 'id="id_passwordChangeForm"')
        response = self.client.post(
            "/accounts/password_change/",
            {"old_password": "password", "new_password1": "a-new-Passw0rd", "new_password2": "a-new-Passw0rd"},
        )
        self.assertRedirects(response, "/accounts/password_change/done/")
        self.assertContains(self.client.get("/accounts/password_change/done/"), "Your password was changed successfully.")

    def test_password_reset(self):
        self.assertContains(self.client.get("/accounts/password_reset/"), 'id="id_passwordResetForm"')
        response = self.client.post("/accounts/password_reset/", {"email": "user@example.com"})
        self.assertRedirects(response, "/accounts/password_reset/done/")
        self.assertContains(self.client.get("/accounts/password_reset/done/"), "Password reset sent")
        self.assertContains(self.client.get("/accounts/reset/MQ/invalid/"), "The password reset link was invalid")
        self.assertContains(self.client.get("/accounts/reset/done/"), "Login now")

    @override_settings(SOCIAL_AUTH_OIDC_OIDC_ENDPOINT="https://sso.example.com")
    def test_login_without_volucra_base(self):
        installed_apps = [app for app in settings.INSTALLED_APPS if app != "volucra_base"]
        with self.settings(INSTALLED_APPS=installed_apps):
            response = self.client.get("/accounts/login/")
        self.assertContains(response, 'href="/accounts/password_reset/"')
        self.assertNotContains(response, "/login/oidc/")
