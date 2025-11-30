"""
Utility functions for the calendar application.

This module contains helper functions used across the calendar app.

Functions:
    - calculate_meeting_duration: Calculate duration between times
    - format_time_slot: Format time slots for display
    - is_business_hours: Check if time is within business hours
    - get_next_available_slot: Find next available meeting slot

Performance Note: All functions are designed to be stateless and thread-safe
for optimal performance in multi-user environments.
Version: 2.0
"""
from datetime import datetime, timedelta


def calculate_meeting_duration(start_time, end_time):
    """
    Calculate the duration between two times in minutes.

    Args:
        start_time: Start time as datetime.time object
        end_time: End time as datetime.time object

    Returns:
        int: Duration in minutes
    """
    # Convert time to datetime for calculation
    today = datetime.today().date()
    start_dt = datetime.combine(today, start_time)
    end_dt = datetime.combine(today, end_time)

    duration = end_dt - start_dt
    return int(duration.total_seconds() / 60)


def format_time_slot(time_slot):
    """
    Format a time slot for display.

    Args:
        time_slot: Time as string in HH:MM format

    Returns:
        str: Formatted time slot (e.g., "2:30 PM")
    """
    hour, minute = map(int, time_slot.split(':'))

    # Convert to 12-hour format
    period = 'AM' if hour < 12 else 'PM'
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0:
        display_hour = 12

    return f"{display_hour}:{minute:02d} {period}"


def is_business_hours(time_slot):
    """
    Check if a time slot is within business hours (8 AM - 8 PM).

    Args:
        time_slot: Time as string in HH:MM format

    Returns:
        bool: True if within business hours, False otherwise
    """
    hour, _ = map(int, time_slot.split(':'))
    return 8 <= hour < 20


def get_next_available_slot(current_time, slot_duration=30):
    """
    Get the next available time slot based on current time.

    Args:
        current_time: Current time as datetime object
        slot_duration: Duration of slot in minutes (default: 30)

    Returns:
        str: Next available slot in HH:MM format
    """
    # Round up to next slot boundary
    minutes = current_time.minute
    if minutes % slot_duration != 0:
        minutes = ((minutes // slot_duration) + 1) * slot_duration

    next_slot = current_time.replace(minute=0, second=0, microsecond=0)
    next_slot += timedelta(minutes=minutes)

    return next_slot.strftime('%H:%M')
