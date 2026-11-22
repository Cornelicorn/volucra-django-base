"""Include them e.g. with path("", include("volucra_base.urls")), the theme switcher of tabler_ui finds them by name"""

from django.urls import path

from .views import save_preferences

app_name = "volucra_base"

urlpatterns = [
    path("preferences/", save_preferences, name="save-preferences"),
]
