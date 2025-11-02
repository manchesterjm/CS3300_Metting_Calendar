"""
Django models for the calendar application.

This module defines the database models for tracking unavailability entries
in the meeting scheduler application.
"""
from django.db import models


class Unavailability(models.Model):
    """
    Model representing a time period when someone is unavailable for meetings.

    This model stores date and time ranges during which a user is not available
    for scheduling meetings. Each entry represents a continuous unavailable period
    on a specific date.

    Attributes:
        date: The date of the unavailability (YYYY-MM-DD format).
        start_time: The beginning time of the unavailable period (HH:MM format).
        end_time: The ending time of the unavailable period (HH:MM format).
    """
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        """
        Return a human-readable string representation of the unavailability entry.

        Returns:
            str: Formatted string showing date, start time, and end time.
        """
        return f"{self.date} from {self.start_time} to {self.end_time}"
