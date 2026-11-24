from .urls import urlpatterns as all_urlpatterns

# The test URLs without volucra_base.urls
urlpatterns = [pattern for pattern in all_urlpatterns if getattr(pattern, "app_name", None) != "volucra_base"]
