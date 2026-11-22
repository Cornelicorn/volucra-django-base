from django.conf import settings
from django.contrib.auth.models import Group


def assign_groups_and_attributes(backend, user, response, *args, **kwargs):
    """
    Step of the SOCIAL_AUTH_PIPELINE of social-auth-app-django which adds the user to the Django groups named in the
    groups claim of OpenID Connect, creating missing ones. If the setting ADMIN_GROUP is set, members of that group
    become staff and superusers and everyone else loses these rights.
    """
    if backend.name == "oidc":
        groups = response.get("groups", [])

        for group_name in groups:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        admin_group = getattr(settings, "ADMIN_GROUP", None)
        if admin_group is not None:
            if admin_group in groups:
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False

        user.full_clean()
        user.save()
