"""
Django models for the calendar application.

This module defines the database models for tracking unavailability entries
in the meeting scheduler application.
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
