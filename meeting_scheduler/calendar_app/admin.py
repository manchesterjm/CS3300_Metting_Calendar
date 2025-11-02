"""
Django admin configuration for the calendar application.

This module registers models with the Django admin interface for
administrative management of unavailability entries and groups.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Unregister the default User admin
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
