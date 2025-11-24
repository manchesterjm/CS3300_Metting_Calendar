"""
Utility functions for the calendar application.

This module contains helper functions used across the calendar app.

Functions:
    - calculate_meeting_duration: Calculate duration between times
    - format_time_slot: Format time slots for display
    - is_business_hours: Check if time is within business hours
    - get_next_available_slot: Find next available meeting slot
    - generate_password: Generate secure random password
    - calculate_free_time_slots: Calculate free time slots for a date
    - generate_recurring_instances: Generate recurring unavailability instances

Performance Note: All functions are designed to be stateless and thread-safe
for optimal performance in multi-user environments.
Version: 2.2 (Recurring Unavailability Support)
"""
from datetime import datetime, timedelta
import secrets
from django.utils import timezone


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


def generate_password(length=16):
    """
    Generate a cryptographically secure random password with unique characters.

    Based on CS3080 password generation logic. Ensures password contains:
    - At least 2 numbers (2-9, excludes 0 and 1)
    - At least 2 lowercase letters (excludes 'l' and 'i' for clarity)
    - At least 2 uppercase letters (excludes 'O' and 'I' for clarity)
    - At least 2 special characters from: @#$%&?*

    Uses Python's secrets module for cryptographically secure random generation.

    Args:
        length (int): Length of password to generate. Must be >= 8. Default is 16.

    Returns:
        str: A randomly generated password of specified length.

    Raises:
        ValueError: If length is less than 8 or exceeds available unique characters.
    """
    # Define the character sets (matching CS3080 passwords.py logic)
    numbers = [str(num) for num in range(2, 10)]  # 2-9 (no 0, 1)
    lower = [chr(i) for i in range(ord('a'), ord('z') + 1) if chr(i) not in ('l', 'i')]  # a-z except l, i
    upper = [chr(i) for i in range(ord('A'), ord('Z') + 1) if chr(i) not in ('O', 'I')]  # A-Z except O, I
    punct = ['@', '#', '$', '%', '&', '?', '*']  # Special characters

    # Validate password length
    total_unique_chars = len(set(numbers + lower + upper + punct))
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")
    if length > total_unique_chars:
        raise ValueError(f"Password length cannot exceed {total_unique_chars} (total unique characters).")

    # Sample 2 unique characters from each category using secrets module
    password_chars = []

    # Add 2 unique numbers
    available_numbers = numbers.copy()
    for _ in range(2):
        char = secrets.choice(available_numbers)
        password_chars.append(char)
        available_numbers.remove(char)

    # Add 2 unique lowercase letters
    available_lower = lower.copy()
    for _ in range(2):
        char = secrets.choice(available_lower)
        password_chars.append(char)
        available_lower.remove(char)

    # Add 2 unique uppercase letters
    available_upper = upper.copy()
    for _ in range(2):
        char = secrets.choice(available_upper)
        password_chars.append(char)
        available_upper.remove(char)

    # Add 2 unique special characters
    available_punct = punct.copy()
    for _ in range(2):
        char = secrets.choice(available_punct)
        password_chars.append(char)
        available_punct.remove(char)

    # Get remaining characters needed to reach desired length
    all_chars = numbers + lower + upper + punct
    remaining_needed = length - 8

    for _ in range(remaining_needed):
        # Pick from all available chars, may include duplicates
        char = secrets.choice(all_chars)
        password_chars.append(char)

    # Shuffle the password using Fisher-Yates shuffle with secrets module
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    # Convert list to string
    return ''.join(password_chars)


def calculate_free_time_slots(selected_date, unavail_list):
    """
    Calculate free 30-minute time slots for a given date.

    Generates all possible 30-minute slots between 8:00 and 20:00,
    then removes slots that conflict with unavailability entries.

    Uses timezone-aware datetime objects for correct timezone handling.

    Args:
        selected_date: Date to calculate free times for (datetime.date object)
        unavail_list: QuerySet or list of Unavailability objects for that date

    Returns:
        list: List of free time slots as strings in "HH:MM" format
    """
    # Generate all possible 30-minute slots from 8:00 to 20:00
    # Use timezone-aware datetime objects
    start_dt = timezone.make_aware(
        datetime.combine(selected_date, datetime.min.time().replace(hour=8))
    )
    end_dt = timezone.make_aware(
        datetime.combine(selected_date, datetime.min.time().replace(hour=20))
    )
    all_slots = []
    while start_dt < end_dt:
        all_slots.append(start_dt.time())
        start_dt += timedelta(minutes=30)

    # Mark taken slots based on unavailability entries
    taken_slots = set()
    for unavail in unavail_list:
        # Use timezone-aware datetimes for unavailability period
        current_slot = timezone.make_aware(
            datetime.combine(selected_date, unavail.start_time)
        )
        unavail_end = timezone.make_aware(
            datetime.combine(selected_date, unavail.end_time)
        )
        while current_slot < unavail_end:
            taken_slots.add(current_slot.time())
            current_slot += timedelta(minutes=30)

    # Calculate free times (times when NO one is unavailable)
    free_times = [slot.strftime("%H:%M") for slot in all_slots
                  if slot not in taken_slots]

    return free_times


def generate_recurring_instances(recurring_entry, days_ahead=90):
    """
    Generate recurring unavailability instances based on a recurrence pattern.

    Creates individual Unavailability entries for each occurrence of a recurring
    pattern over the next N days. All generated instances link back to the parent
    via the parent_recurring_entry field.

    Args:
        recurring_entry: Unavailability model instance with is_recurring=True
                        and a populated recurrence_pattern JSONField
        days_ahead: Number of days into the future to generate instances (default: 90)

    Returns:
        list: List of created Unavailability instances

    Raises:
        ValueError: If recurring_entry is not marked as recurring or has no pattern

    Recurrence Pattern Format:
        {
            "frequency": "daily" | "weekly" | "monthly",
            "days": ["monday", "wednesday", "friday"],  # For weekly frequency
            "interval": 1,  # Every N days/weeks/months
            "end_date": "2026-12-31"  # Optional end date (YYYY-MM-DD)
        }

    Example:
        pattern = {
            "frequency": "weekly",
            "days": ["monday", "wednesday", "friday"],
            "interval": 1,
            "end_date": "2026-06-30"
        }
        instances = generate_recurring_instances(recurring_entry, days_ahead=90)
    """
    # Validate inputs
    if not recurring_entry.is_recurring:
        raise ValueError("Entry must be marked as recurring (is_recurring=True)")
    if not recurring_entry.recurrence_pattern:
        raise ValueError("Entry must have a recurrence_pattern defined")

    pattern = recurring_entry.recurrence_pattern
    frequency = pattern.get('frequency', 'weekly')
    interval = pattern.get('interval', 1)
    end_date_str = pattern.get('end_date')

    # Parse end date if provided
    end_date = None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Invalid date format, ignore end_date
            end_date = None

    # Calculate the limit date (90 days from now or end_date, whichever is sooner)
    start_date = recurring_entry.date
    limit_date = start_date + timedelta(days=days_ahead)
    if end_date and end_date < limit_date:
        limit_date = end_date

    instances = []
    current_date = start_date

    # Day name mapping for weekly recurrence
    day_names = {
        0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
        4: 'friday', 5: 'saturday', 6: 'sunday'
    }

    # Import here to avoid circular import
    from calendar_app.models import Unavailability  # pylint: disable=import-outside-toplevel

    while current_date <= limit_date:
        should_create = False

        if frequency == 'daily':
            # Create an instance every N days
            days_diff = (current_date - start_date).days
            if days_diff % interval == 0:
                should_create = True

        elif frequency == 'weekly':
            # Create instances on specified weekdays
            weekday_name = day_names[current_date.weekday()]
            days_list = pattern.get('days', [])
            if weekday_name in days_list:
                # Check if this week matches the interval
                weeks_diff = (current_date - start_date).days // 7
                if weeks_diff % interval == 0:
                    should_create = True

        elif frequency == 'monthly':
            # Create instance on the same day of month every N months
            if current_date.day == start_date.day:
                months_diff = (current_date.year - start_date.year) * 12 + \
                              (current_date.month - start_date.month)
                if months_diff % interval == 0:
                    should_create = True

        # Create the instance if conditions met (skip the original start_date)
        if should_create and current_date != start_date:
            instance = Unavailability.objects.create(
                user=recurring_entry.user,
                date=current_date,
                start_time=recurring_entry.start_time,
                end_time=recurring_entry.end_time,
                description=recurring_entry.description,
                is_recurring=False,  # Individual instances are not recurring
                recurrence_pattern=None,
                parent_recurring_entry=recurring_entry
            )
            instances.append(instance)

        # Move to next day
        current_date += timedelta(days=1)

    return instances
