from django.urls import path

from .views import set_theme

app_name = "tabler_ui"

urlpatterns = [
    path("theme/", set_theme, name="set-theme"),
]
