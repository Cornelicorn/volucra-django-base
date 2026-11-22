from django.contrib import admin

from .models import UserPreferences


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "theme")
    list_filter = ("theme",)
    search_fields = ("user__username",)
