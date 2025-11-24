"""
Django admin configuration for the calendar application.

This module registers models with the Django admin interface for
administrative management of unavailability entries and groups.

IMPORTANT: Admin User Customization Pattern
-------------------------------------------
This module uses an unregister/re-register pattern to customize Django's
built-in User admin interface. This approach has both benefits and risks:

BENEFITS:
- Allows adding custom functionality (password generation template)
- No need to create a custom User model (keeps Django defaults)
- Minimal changes to existing User model

RISKS & CONSIDERATIONS:
- May conflict with other Django apps that customize User admin
- Order of app loading in INSTALLED_APPS matters (this should load LAST)
- Django admin may raise AlreadyRegistered exception if not careful

ALTERNATIVES (if conflicts occur):
1. Create a custom User model (recommended for larger projects)
2. Coordinate all User admin customizations in a single app
3. Use admin.site.unregister() only in one location across entire project
4. Check settings.INSTALLED_APPS order (calendar_app should be last)

CURRENT STATUS:
- This is the ONLY app in the project customizing User admin (✓ Safe)
- No conflicts expected as this is a standalone educational project
- Documented in STYLE_GUIDE.md and this module

If adding more apps that need User admin customization, refactor to use
a custom User model or centralize admin customizations.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Group, Unavailability, GroupUnavailability

# Unregister Django's default User admin interface
# This allows us to register our custom version below
admin.site.unregister(User)


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom User admin with password generation functionality.

    Extends Django's UserAdmin to add password generation support
    in the admin panel for user password resets. The custom template
    provides a "Generate Password" button for administrators.

    Template Override:
        change_user_password_template: Uses custom template with JavaScript
        password generation (see templates/admin/auth/user/change_password.html)

    Usage:
        Admin users can click "Generate Password" when resetting a user's
        password, which creates a secure random password automatically.

    Security:
        - Uses POST requests for password generation (CSRF protected)
        - Generates 16-character passwords with mixed character types
        - Only accessible to staff users with appropriate permissions
    """
    change_user_password_template = 'admin/auth/user/change_password.html'


# Re-register User model with our custom admin class
# NOTE: This must be the ONLY place in the project where User admin is registered
# Multiple registrations will cause Django to raise AlreadyRegistered exception
admin.site.register(User, CustomUserAdmin)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Admin interface for Group model with join code management.

    Displays group information including join codes and their enabled status.
    Allows admins to view and manage group join codes directly from the admin panel.

    List Display:
        - name: Group name
        - created_by: User who created the group
        - created_at: When the group was created
        - join_code: The group's join code (if any)
        - join_code_enabled: Whether the join code is active

    Filters:
        - created_by: Filter by group owner
        - join_code_enabled: Filter by code status (enabled/disabled)

    Search:
        - Searchable by group name and join code
    """
    list_display = ('name', 'created_by', 'created_at', 'join_code', 'join_code_enabled')
    list_filter = ('created_by', 'join_code_enabled', 'created_at')
    search_fields = ('name', 'join_code')
    readonly_fields = ('created_at',)
    filter_horizontal = ('members',)


@admin.register(Unavailability)
class UnavailabilityAdmin(admin.ModelAdmin):
    """
    Admin interface for personal Unavailability entries.

    Displays individual user unavailability periods with date and time details.
    Allows admins to view and manage user availability schedules.

    List Display:
        - user: User who created the entry
        - date: Date of unavailability
        - start_time: Start time
        - end_time: End time
        - description: Optional description

    Filters:
        - user: Filter by user
        - date: Filter by date

    Search:
        - Searchable by username and description
    """
    list_display = ('user', 'date', 'start_time', 'end_time', 'description')
    list_filter = ('user', 'date')
    search_fields = ('user__username', 'description')
    ordering = ('-date', '-start_time')


@admin.register(GroupUnavailability)
class GroupUnavailabilityAdmin(admin.ModelAdmin):
    """
    Admin interface for group unavailability entries.

    Displays group unavailability periods created by group members.
    Allows admins to view and manage group scheduling conflicts.

    List Display:
        - group: Group name
        - user: User who created the entry
        - date: Date of unavailability
        - start_time: Start time
        - end_time: End time
        - description: Optional description

    Filters:
        - group: Filter by group
        - user: Filter by user
        - date: Filter by date

    Search:
        - Searchable by group name, username, and description
    """
    list_display = ('group', 'user', 'date', 'start_time', 'end_time', 'description')
    list_filter = ('group', 'user', 'date')
    search_fields = ('group__name', 'user__username', 'description')
    ordering = ('-date', '-start_time')
