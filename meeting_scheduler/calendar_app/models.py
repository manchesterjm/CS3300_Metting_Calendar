"""
Django models for the calendar application.

This module defines the database models for tracking unavailability entries
in the meeting scheduler application, including support for shared group calendars.

Models:
    - Unavailability: Individual user unavailability periods
    - Group: Shared calendar groups for team scheduling
    - GroupUnavailability: Unavailability entries for group calendars
    - MeetingProposal: Proposed meeting times for group coordination
    - MeetingResponse: Member responses to meeting proposals

Version: 3.0 (Meeting Proposals Support)
Last Updated: 2025-11-24
"""
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def validate_recurrence_pattern(value):
    """
    Validate recurrence_pattern JSON structure.

    Security: Prevents malicious or malformed JSON patterns from causing application
    crashes, infinite loops, or logic bypasses. Validates structure, data types,
    and value ranges for all pattern fields.

    Args:
        value: JSON object (dict) containing recurrence pattern configuration

    Raises:
        ValidationError: If pattern structure or values are invalid

    Valid Pattern Structure:
        {
            "frequency": "daily" | "weekly" | "monthly",
            "interval": 1-52 (integer),
            "days": ["monday", "tuesday", ...],  # Required for weekly
            "end_date": "YYYY-MM-DD"  # Optional
        }
    """
    if value is None:
        return  # Null is allowed for non-recurring entries

    # Validate value is a dictionary
    if not isinstance(value, dict):
        raise ValidationError(
            'recurrence_pattern must be a JSON object (dictionary), '
            f'got {type(value).__name__}.'
        )

    # Validate frequency field (required)
    frequency = value.get('frequency')
    valid_frequencies = ['daily', 'weekly', 'monthly']
    if frequency not in valid_frequencies:
        raise ValidationError(
            f'Invalid frequency: "{frequency}". Must be one of: '
            f'{", ".join(valid_frequencies)}.'
        )

    # Validate interval field (required)
    interval = value.get('interval', 1)
    if not isinstance(interval, int) or interval < 1 or interval > 52:
        raise ValidationError(
            f'Invalid interval: {interval}. Must be an integer between 1 and 52.'
        )

    # Validate days field (required for weekly frequency)
    if frequency == 'weekly':
        days = value.get('days', [])
        if not isinstance(days, list):
            raise ValidationError(
                f'days must be a list, got {type(days).__name__}.'
            )
        if not days:
            raise ValidationError(
                'days cannot be empty for weekly frequency. '
                'At least one day must be selected.'
            )

        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday',
                      'friday', 'saturday', 'sunday']
        for day in days:
            if not isinstance(day, str):
                raise ValidationError(
                    f'Each day must be a string, got {type(day).__name__} for value: {day}.'
                )
            if day not in valid_days:
                raise ValidationError(
                    f'Invalid day: "{day}". Must be one of: {", ".join(valid_days)}.'
                )

    # Validate end_date format (optional)
    end_date = value.get('end_date')
    if end_date is not None:
        if not isinstance(end_date, str):
            raise ValidationError(
                f'end_date must be a string, got {type(end_date).__name__}.'
            )
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f'Invalid end_date format: "{end_date}". '
                f'Must be YYYY-MM-DD format. Error: {e}'
            ) from e

    # Security: Disallow unknown keys to prevent injection attacks
    allowed_keys = {'frequency', 'interval', 'days', 'end_date'}
    unknown_keys = set(value.keys()) - allowed_keys
    if unknown_keys:
        raise ValidationError(
            f'Unknown keys in recurrence pattern: {", ".join(unknown_keys)}. '
            f'Allowed keys: {", ".join(allowed_keys)}.'
        )


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
    recurrence_pattern = models.JSONField(
        null=True,
        blank=True,
        validators=[validate_recurrence_pattern],
        help_text="JSON pattern defining recurrence schedule (frequency, interval, days, end_date)"
    )
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


class MeetingProposal(models.Model):
    """
    Model representing a proposed meeting time for a group.

    Meeting proposals allow users to suggest specific meeting times. All group
    members must accept the proposal for it to be scheduled. If any member
    declines, the proposal is rejected.

    Attributes:
        group: The group this proposal belongs to.
        proposed_by: The user who created the proposal.
        title: Title/subject of the meeting.
        description: Optional detailed description.
        meeting_datetime: Proposed date and time for the meeting.
        duration_minutes: Duration in minutes (30, 60, or 120).
        status: Current status (pending, accepted, rejected, scheduled).
        created_at: Timestamp when proposal was created.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('scheduled', 'Scheduled'),
    ]

    DURATION_CHOICES = [
        (30, '30 minutes'),
        (60, '1 hour'),
        (120, '2 hours'),
    ]

    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='meeting_proposals'
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proposed_meetings'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    meeting_datetime = models.DateTimeField()
    duration_minutes = models.IntegerField(choices=DURATION_CHOICES, default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group', 'status']),
            models.Index(fields=['proposed_by', 'status']),
            models.Index(fields=['meeting_datetime']),
        ]

    def __str__(self):
        """
        Return a human-readable string representation of the meeting proposal.

        Returns:
            str: Formatted string showing title, group, and datetime.
        """
        return f"{self.title} - {self.group.name} at {self.meeting_datetime}"

    def get_all_responses(self):
        """
        Get all responses to this proposal.

        Returns:
            QuerySet: All MeetingResponse objects for this proposal.
        """
        return self.responses.all()

    def get_pending_members(self):
        """
        Get list of group members and owner who haven't responded yet.

        Security: Includes group owner to ensure they can participate in proposals.
        Without this, owner-only groups or groups where owner hasn't responded
        would incorrectly auto-schedule meetings.

        Returns:
            QuerySet: User objects who are group members or owner but haven't responded.
        """
        from django.contrib.auth import get_user_model
        user_model = get_user_model()

        responded_user_ids = self.responses.values_list('user_id', flat=True)
        # Get all members + owner (using distinct to avoid duplicates if owner is also member)
        member_ids = list(self.group.members.values_list('id', flat=True))
        owner_id = self.group.created_by.id
        all_participant_ids = list(set(member_ids + [owner_id]))

        # Return users who haven't responded
        return user_model.objects.filter(id__in=all_participant_ids).exclude(id__in=responded_user_ids)

    def check_all_accepted(self):
        """
        Check if all group members and owner have accepted the proposal.

        Security: Counts owner + members to prevent auto-scheduling without owner's consent.
        Without this check, meetings could be scheduled even if the owner (who may have
        created the proposal) hasn't explicitly accepted.

        Returns:
            bool: True if all members and owner accepted, False otherwise.
        """
        # Count unique participants (owner + members, avoiding duplicates)
        member_ids = set(self.group.members.values_list('id', flat=True))
        owner_id = self.group.created_by.id
        all_participant_ids = member_ids | {owner_id}  # Set union
        total_participants = len(all_participant_ids)

        accepted_count = self.responses.filter(response='accept').count()
        return total_participants > 0 and total_participants == accepted_count

    def has_rejection(self):
        """
        Check if any member has declined the proposal.

        Returns:
            bool: True if at least one decline response exists.
        """
        return self.responses.filter(response='decline').exists()

    def user_can_view(self, user):
        """
        Check if a user can view this proposal.

        Args:
            user: The User instance to check permissions for.

        Returns:
            bool: True if user is a group member or owner.
        """
        return self.group.user_can_view(user)

    def user_can_respond(self, user):
        """
        Check if a user can respond to this proposal.

        Security: Allows both group members AND owner to respond. Without this check,
        the owner who created the proposal couldn't accept it themselves, leading to
        meetings that can never be scheduled in owner-only groups.

        Args:
            user: The User instance to check permissions for.

        Returns:
            bool: True if user is a group member or owner and hasn't responded yet.
        """
        # User must be either owner or member
        is_participant = self.group.is_member(user) or self.group.is_owner(user)
        if not is_participant:
            return False
        return not self.responses.filter(user=user).exists()


class MeetingResponse(models.Model):
    """
    Model representing a user's response to a meeting proposal.

    Each group member can respond once to a proposal with accept or decline.

    Attributes:
        proposal: The meeting proposal this response belongs to.
        user: The user who submitted this response.
        response: Accept or decline.
        responded_at: Timestamp when response was submitted.
    """
    RESPONSE_CHOICES = [
        ('accept', 'Accept'),
        ('decline', 'Decline'),
    ]

    proposal = models.ForeignKey(
        'MeetingProposal',
        on_delete=models.CASCADE,
        related_name='responses'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meeting_responses'
    )
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['proposal', 'user']
        ordering = ['-responded_at']
        indexes = [
            models.Index(fields=['proposal', 'response']),
            models.Index(fields=['user', 'responded_at']),
        ]

    def __str__(self):
        """
        Return a human-readable string representation of the response.

        Returns:
            str: Formatted string showing user, response, and proposal.
        """
        action = "accepted" if self.response == "accept" else "declined"
        return f"{self.user.username} {action}: {self.proposal.title}"
