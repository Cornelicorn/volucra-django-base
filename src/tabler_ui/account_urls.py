"""
The login, logout, password change and password reset pages. Include them without a namespace, as Django refers to
them by their plain names, e.g. path("accounts/", include("tabler_ui.account_urls")).
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm


def template(name: str) -> str:
    return f"tabler_ui/registration/{name}.html"


urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=LoginForm, template_name=template("login")),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name=template("logged_out")),
        name="logout",
    ),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(form_class=PasswordChangeForm, template_name=template("password_change_form")),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name=template("password_change_done")),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(form_class=PasswordResetForm, template_name=template("password_reset_form")),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name=template("password_reset_done")),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=SetPasswordForm, template_name=template("password_reset_confirm")
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name=template("password_reset_complete")),
        name="password_reset_complete",
    ),
]
