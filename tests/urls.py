from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", include("social_django.urls", namespace="social")),
    path("admin/", admin.site.urls),
    path("accounts/", include("tabler_ui.account_urls")),
    path("ui/", include("tabler_ui.urls")),
    path("groups/", views.GroupListView.as_view(), name="group-list"),
    path("groups/create", views.GroupCreateView.as_view(), name="group-create"),
    path("groups/<int:pk>", views.GroupDetailView.as_view(), name="group-detail"),
    path("groups/<int:pk>/edit", views.GroupEditView.as_view(), name="group-edit"),
    path("groups/<int:pk>/delete", views.GroupDeleteView.as_view(), name="group-delete"),
]
