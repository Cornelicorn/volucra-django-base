from types import SimpleNamespace

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.checks import run_checks
from django.test import TestCase, override_settings

from volucra_base.auth_pipeline.oidc import assign_groups_and_attributes
from volucra_base.preferences import registry


class SSOTests(TestCase):
    def test_no_sso_button_without_endpoint(self):
        self.assertNotContains(self.client.get("/accounts/login/"), "Volucra SSO")
        self.assertNotContains(self.client.get("/admin/login/"), "Volucra SSO")

    @override_settings(SOCIAL_AUTH_OIDC_OIDC_ENDPOINT="https://sso.example.com")
    def test_sso_buttons(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, 'action="/login/oidc/"')
        self.assertContains(response, "Volucra SSO")

        response = self.client.get("/admin/login/")
        self.assertContains(response, 'action="/login/oidc/"')
        self.assertContains(response, 'value="Volucra SSO"')

    @override_settings(SOCIAL_AUTH_OIDC_OIDC_ENDPOINT="https://sso.example.com", VOLUCRA_SSO_LABEL="Company login")
    def test_sso_label(self):
        self.assertContains(self.client.get("/accounts/login/"), "Company login")

    @override_settings(SOCIAL_AUTH_OIDC_OIDC_ENDPOINT="https://sso.example.com")
    def test_sso_button_comes_after_reset_password(self):
        html = self.client.get("/accounts/login/").content.decode()
        self.assertLess(html.index('href="/accounts/password_reset/"'), html.index('action="/login/oidc/"'))


class AppOrderCheckTests(TestCase):
    def test_no_warning_when_volucra_base_comes_first(self):
        self.assertEqual([e.id for e in run_checks() if e.id.startswith("volucra_base")], [])

    def test_warning_when_volucra_base_comes_later(self):
        installed_apps = [
            "tabler_ui",
            "django.contrib.admin",
            "volucra_base",
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
        ]
        with self.settings(INSTALLED_APPS=installed_apps):
            warnings = [e for e in run_checks() if e.id == "volucra_base.W001"]
        self.assertEqual(len(warnings), 2)
        self.assertIn("before tabler_ui", warnings[0].hint)
        self.assertIn("before django.contrib.admin", warnings[1].hint)


class WithoutTablerUITests(TestCase):
    @override_settings(SOCIAL_AUTH_OIDC_OIDC_ENDPOINT="https://sso.example.com")
    def test_volucra_base_on_its_own(self):
        installed_apps = [app for app in settings.INSTALLED_APPS if app != "tabler_ui"]
        with self.settings(INSTALLED_APPS=installed_apps):
            self.assertNotIn("tabler_ui.theme", registry)
            self.assertIn("prefapp.page_size", registry)
            self.assertEqual([e.id for e in run_checks() if e.id.startswith("volucra_base")], [])
            self.assertContains(self.client.get("/admin/login/"), 'action="/login/oidc/"')


class OIDCPipelineTests(TestCase):
    oidc = SimpleNamespace(name="oidc")

    def setUp(self):
        self.user = User.objects.create_user("user", password="password")

    @override_settings(ADMIN_GROUP="admins")
    def test_groups_and_admin_rights(self):
        assign_groups_and_attributes(self.oidc, self.user, {"groups": ["admins", "players"]})
        self.user.refresh_from_db()
        self.assertEqual(set(self.user.groups.values_list("name", flat=True)), {"admins", "players"})
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)

        assign_groups_and_attributes(self.oidc, self.user, {"groups": ["players"]})
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    @override_settings(ADMIN_GROUP=None)
    def test_admin_rights_are_left_alone_without_admin_group(self):
        self.user.is_staff = True
        self.user.save()
        assign_groups_and_attributes(self.oidc, self.user, {"groups": []})
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)

    def test_other_backends_are_ignored(self):
        assign_groups_and_attributes(SimpleNamespace(name="github"), self.user, {"groups": ["players"]})
        self.assertFalse(Group.objects.exists())
