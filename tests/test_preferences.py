from typing import ClassVar

from django import forms
from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import TestCase, override_settings

from volucra_base.admin import UserPreferencesForm
from volucra_base.models import UserPreferences
from volucra_base.preferences import PreferenceRegistry, get_preferences, get_save_url, registry


class ShopConfig(AppConfig):
    """An app which isn't installed, the tests pass subclasses declaring preferences to the registry themselves"""

    # Without a module Django can't find the path of the app
    path = "/shop"


class RegistryTests(TestCase):
    def test_preferences_of_all_apps_by_app_label(self):
        self.assertIn("tabler_ui.theme", registry)
        self.assertIn("prefapp.notifications", registry)
        self.assertIn("prefapp.page_size", registry)
        self.assertIsInstance(registry["prefapp.page_size"], forms.IntegerField)

    def test_registry_follows_the_installed_apps(self):
        installed_apps = [app for app in settings.INSTALLED_APPS if app != "tests.prefapp"]
        with self.settings(INSTALLED_APPS=installed_apps):
            self.assertNotIn("prefapp.page_size", registry)
            self.assertIn("tabler_ui.theme", registry)
        self.assertIn("prefapp.page_size", registry)

    def test_get_user_preferences_takes_precedence(self):
        class Config(ShopConfig):
            user_preferences: ClassVar[dict[str, forms.Field]] = {"ignored": forms.BooleanField(required=False)}

            def get_user_preferences(self) -> dict[str, forms.Field]:
                return {"newsletter": forms.BooleanField(required=False, initial=False)}

        self.assertEqual(list(PreferenceRegistry.collect([Config("shop", None)])), ["shop.newsletter"])

    def test_declarations_have_to_be_form_fields(self):
        class Config(ShopConfig):
            user_preferences: ClassVar[dict[str, object]] = {"newsletter": True}

        with self.assertRaisesMessage(ImproperlyConfigured, "shop.newsletter has to be a form field"):
            PreferenceRegistry.collect([Config("shop", None)])

    def test_defaults_have_to_be_valid(self):
        class Config(ShopConfig):
            user_preferences: ClassVar[dict[str, forms.Field]] = {"size": forms.IntegerField(min_value=5, initial=1)}

        with self.assertRaisesMessage(ImproperlyConfigured, "The default 1 of the preference shop.size is invalid"):
            PreferenceRegistry.collect([Config("shop", None)])

    def test_registry_is_read_only(self):
        with self.assertRaises(TypeError):
            registry.load()["shop.newsletter"] = forms.BooleanField()  # type: ignore[index]


class PreferencesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", password="password")

    def test_defaults(self):
        preferences = get_preferences(self.user)
        self.assertEqual(preferences["tabler_ui.theme"], "auto")
        self.assertIs(preferences["prefapp.notifications"], True)
        self.assertEqual(preferences["prefapp.page_size"], 25)
        self.assertIsNone(preferences.get_chosen("tabler_ui.theme"))
        self.assertFalse(UserPreferences.objects.exists())

    def test_preferences_of_all_apps_are_kept_in_one_row(self):
        get_preferences(self.user).update({"tabler_ui.theme": "dark"})
        get_preferences(self.user).update({"prefapp.page_size": "50", "prefapp.notifications": "false"})

        self.assertEqual(UserPreferences.objects.count(), 1)
        self.assertEqual(
            UserPreferences.objects.get(user=self.user).values,
            {"tabler_ui.theme": "dark", "prefapp.page_size": 50, "prefapp.notifications": False},
        )
        preferences = get_preferences(User.objects.get(pk=self.user.pk))
        self.assertEqual(preferences["tabler_ui.theme"], "dark")
        self.assertEqual(preferences["prefapp.page_size"], 50)
        self.assertIs(preferences["prefapp.notifications"], False)
        self.assertEqual(preferences.get_chosen("tabler_ui.theme"), "dark")

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValidationError) as context:
            get_preferences(self.user).update({"tabler_ui.theme": "pink", "prefapp.page_size": "1", "shop.size": "2"})
        self.assertEqual(set(context.exception.message_dict), {"tabler_ui.theme", "prefapp.page_size", "shop.size"})
        self.assertFalse(UserPreferences.objects.exists())

    def test_values_which_became_invalid_fall_back_to_the_default(self):
        UserPreferences.objects.create(
            user=self.user, values={"tabler_ui.theme": "sepia", "prefapp.page_size": 30, "removed.app": 1}
        )
        preferences = get_preferences(self.user)
        self.assertIsNone(preferences.get_chosen("tabler_ui.theme"))
        self.assertEqual(preferences["tabler_ui.theme"], "auto")
        self.assertEqual(preferences["prefapp.page_size"], 30)

    def test_unknown_preferences(self):
        with self.assertRaises(KeyError):
            get_preferences(self.user)["shop.newsletter"]

    def test_preferences_are_loaded_once_per_user_object(self):
        UserPreferences.objects.create(user=self.user, values={"tabler_ui.theme": "dark"})
        for user in User.objects.get(pk=self.user.pk), self.user_without_preferences():
            with self.subTest(user=user.username), self.assertNumQueries(1):
                get_preferences(user)["tabler_ui.theme"]
                get_preferences(user)["prefapp.page_size"]

    def test_changes_are_seen_by_the_user_object(self):
        UserPreferences.objects.create(user=self.user, values={"tabler_ui.theme": "dark"})
        for user in User.objects.get(pk=self.user.pk), self.user_without_preferences():
            with self.subTest(user=user.username):
                # Caches the row of the user, or that there is none, on the user object
                get_preferences(user)["tabler_ui.theme"]
                get_preferences(user).update({"tabler_ui.theme": "light"})
                with self.assertNumQueries(0):
                    self.assertEqual(get_preferences(user)["tabler_ui.theme"], "light")

    def user_without_preferences(self):
        return User.objects.create_user("other", password="password")

    def test_anonymous_users_have_the_defaults(self):
        preferences = get_preferences(AnonymousUser())
        self.assertEqual(preferences["tabler_ui.theme"], "auto")
        with self.assertRaises(ValueError):
            preferences.update({"tabler_ui.theme": "dark"})


class SavePreferencesViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", password="password")

    def test_theme_switcher_saves_the_theme(self):
        self.client.force_login(self.user)
        response = self.client.post("/preferences/", {"tabler_ui.theme": "dark"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(UserPreferences.objects.get(user=self.user).values, {"tabler_ui.theme": "dark"})

        self.client.post("/preferences/", {"tabler_ui.theme": "light"})
        self.assertEqual(UserPreferences.objects.get(user=self.user).values, {"tabler_ui.theme": "light"})

    def test_several_preferences_at_once(self):
        self.client.force_login(self.user)
        response = self.client.post("/preferences/", {"prefapp.page_size": "10", "prefapp.notifications": "false"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            UserPreferences.objects.get(user=self.user).values, {"prefapp.page_size": 10, "prefapp.notifications": False}
        )

    def test_errors_by_key(self):
        self.client.force_login(self.user)
        response = self.client.post("/preferences/", {"tabler_ui.theme": "pink", "shop.newsletter": "on"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()["errors"]), {"tabler_ui.theme", "shop.newsletter"})
        self.assertEqual(self.client.post("/preferences/").status_code, 400)
        self.assertFalse(UserPreferences.objects.exists())

    def test_anonymous_users_save_nothing(self):
        response = self.client.post("/preferences/", {"tabler_ui.theme": "dark"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(UserPreferences.objects.exists())

    def test_save_url(self):
        self.assertEqual(get_save_url(), "/preferences/")
        with override_settings(ROOT_URLCONF="tests.urls_without_preferences"):
            self.assertIsNone(get_save_url())

    def test_only_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/preferences/", {"tabler_ui.theme": "dark"}).status_code, 405)

    def test_csrf_token_is_needed(self):
        client = self.client_class(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post("/preferences/", {"tabler_ui.theme": "dark"}).status_code, 403)


class AdminFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", password="password")

    def test_values_are_validated(self):
        form = UserPreferencesForm(
            data={"user": self.user.pk, "values": '{"tabler_ui.theme": "dark", "prefapp.page_size": "40"}'}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().values, {"tabler_ui.theme": "dark", "prefapp.page_size": 40})

    def test_invalid_values(self):
        form = UserPreferencesForm(data={"user": self.user.pk, "values": '{"tabler_ui.theme": "pink", "shop.size": 1}'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors["values"]), 2)

        form = UserPreferencesForm(data={"user": self.user.pk, "values": "[1, 2]"})
        self.assertFalse(form.is_valid())

    def test_admin_page(self):
        admin = User.objects.create_superuser("admin", password="password")
        self.client.force_login(admin)
        UserPreferences.objects.create(user=self.user, values={"tabler_ui.theme": "dark"})
        self.assertContains(self.client.get("/admin/volucra_base/userpreferences/"), "user")
