"""
Django models for the calendar application.

This module defines the database models for tracking unavailability entries
in the meeting scheduler application, including support for shared group calendars.

Models:
    - Unavailability: Individual user unavailability periods
    - Group: Shared calendar groups for team scheduling
    - GroupUnavailability: Unavailability entries for group calendars

Version: 2.0 (Group Calendar Support)
Last Updated: 2025-01-11
"""
from django.conf import settings
from django.db import models


class Unavailability(models.Model):
    """
    Model representing a time period when someone is unavailable for meetings.

    This model stores date and time ranges during which a user is not available
    for scheduling meetings. Each entry represents a continuous unavailable period
    on a specific date and is associated with a specific user.

    Supports recurring unavailability patterns (e.g., "Every Monday 9:00-17:00").

    Attributes:
        user: The user who created this unavailability entry.
        date: The date of the unavailability (YYYY-MM-DD format).
        start_time: The beginning time of the unavailable period (HH:MM format).
        end_time: The ending time of the unavailable period (HH:MM format).
        description: Optional description of the unavailability (e.g., "Doctor appointment").
        is_recurring: Whether this entry is part of a recurring pattern (default: False).
        recurrence_pattern: JSON data defining recurrence (frequency, days, end_date, interval).
        parent_recurring_entry: Link to the master recurring entry that spawned this instance.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='unavailabilities'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=200, blank=True, default='')
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(null=True, blank=True)
    parent_recurring_entry = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='recurring_instances'
    )

    class Meta:
        verbose_name_plural = "Unavailabilities"
        ordering = ['-date', '-start_time']

    def __str__(self):
        """
        Return a human-readable string representation of the unavailability entry.

        Returns:
            str: Formatted string showing user, date, start time, and end time.
        """
        return f"{self.user.username}: {self.date} from {self.start_time} to {self.end_time}"

    def user_can_edit(self, user):
        """
        Check if a user has permission to edit or delete this unavailability entry.

        Only the user who created the entry can edit or delete it.

        Args:
            user: The User instance to check permissions for.

        Returns:
            bool: True if the user can edit this entry, False otherwise.
        """
        return self.user == user


class Group(models.Model):
    """
    Model representing a group that can share calendar information.

    Groups allow multiple users to collaborate on a shared calendar where they can
    see each other's unavailability and collectively manage scheduling.

    Attributes:
        name: Unique name of the group.
        created_by: User who created the group (group owner).
        created_at: Timestamp when the group was created.
        members: Many-to-many relationship with User model for group membership.
        join_code: Optional 8-character alphanumeric code for easy group joining.
        join_code_enabled: Whether the join code is currently active for use.
    """
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='calendar_groups',
        blank=True
    )
    join_code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        help_text="8-character code for joining this group"
    )
    join_code_enabled = models.BooleanField(
        default=True,
        help_text="Whether the join code is currently active"
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        """
        Return the group name as string representation.

        Returns:
            str: The group name.
        """
        return str(self.name)

    def is_member(self, user):
        """
        Check if a user is a member of this group.

        Args:
            user: The User instance to check.

        Returns:
            bool: True if the user is a member, False otherwise.
        """
        return self.members.filter(id=user.id).exists()

    def is_owner(self, user):
        """
        Check if a user is the owner of this group.

        Args:
            user: The User instance to check.

        Returns:
            bool: True if the user is the owner, False otherwise.
        """
        return self.created_by == user

    def user_can_edit(self, user):
        """
        Check if a user has permission to edit this group.

        Only the group owner (creator) can edit or delete the group.

        Args:
            user: The User instance to check permissions for.

        Returns:
            bool: True if the user can edit this group, False otherwise.
        """
        return self.is_owner(user)

    def user_can_view(self, user):
        """
        Check if a user has permission to view this group.

        Both members and owners can view the group.

        Args:
            user: The User instance to check permissions for.

        Returns:
            bool: True if the user can view this group, False otherwise.
        """
        return self.is_member(user) or self.is_owner(user)


class GroupUnavailability(models.Model):
    """
    Model representing unavailability entries for group calendars.

    Unlike personal Unavailability, these entries are tied to a group and visible
    to all group members. Each entry tracks which user created it to enforce
    deletion permissions (only the creator can delete their entry).

    Attributes:
        group: The group this unavailability belongs to.
        user: The user who created this entry (for deletion control).
        date: The date of unavailability (YYYY-MM-DD format).
        start_time: The beginning time of the unavailable period (HH:MM format).
        end_time: The ending time of the unavailable period (HH:MM format).
        description: Optional description of the unavailability (e.g., "Meeting").
    """
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='unavailabilities'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_unavailabilities'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        verbose_name_plural = "Group Unavailabilities"
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['group', 'date']),
            models.Index(fields=['user', 'group']),
        ]

    def __str__(self):
        """
        Return a human-readable string representation of the group unavailability entry.

        Returns:
            str: Formatted string showing group, user, date, and times.
        """
        return f"{self.group.name} - {self.user.username}: {self.date} from {self.start_time} to {self.end_time}"

    def user_can_edit(self, user):
        """
        Check if a user has permission to edit or delete this group unavailability entry.

        Only the user who created the entry can edit or delete it.

        Args:
            user: The User instance to check permissions for.

        Returns:
            bool: True if the user can edit this entry, False otherwise.
        """
        return self.user == user

    def user_can_view(self, user):
        """
        Check if a user has permission to view this group unavailability entry.

        All members of the group can view the entry.

        Args:
            user: The User instance to check permissions for.

        Returns:
            bool: True if the user can view this entry, False otherwise.
        """
        return self.group.user_can_view(user)
