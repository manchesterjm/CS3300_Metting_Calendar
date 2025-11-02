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

    Attributes:
        user: The user who created this unavailability entry.
        date: The date of the unavailability (YYYY-MM-DD format).
        start_time: The beginning time of the unavailable period (HH:MM format).
        end_time: The ending time of the unavailable period (HH:MM format).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='unavailabilities'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

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
    description = models.CharField(max_length=200, blank=True)

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
