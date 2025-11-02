"""
Django admin configuration for the calendar application.

This module registers models with the Django admin interface for
administrative management of unavailability entries and groups.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Unregister the default User admin and register custom version
# NOTE: This unregister/re-register pattern may cause conflicts if other apps
# in this project also customize the User admin. If conflicts occur, consider:
# 1. Coordinating admin customizations in a single location
# 2. Using a custom user model instead of extending the default
# 3. Ensuring this app loads after other apps that modify User admin
admin.site.unregister(User)


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom User admin with password generation functionality.

    Extends Django's UserAdmin to add password generation support
    in the admin panel for user password resets.
    """
    change_password_template = 'admin/auth/user/change_password.html'


# Re-register User with custom admin
admin.site.register(User, CustomUserAdmin)
