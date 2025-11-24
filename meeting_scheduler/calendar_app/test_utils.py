"""
Unit tests for calendar utility functions.

This module contains comprehensive tests for the utility functions
used across the calendar application.

Test Classes:
    - CalculateMeetingDurationTests: Test duration calculations
    - FormatTimeSlotTests: Test time slot formatting
    - IsBusinessHoursTests: Test business hours validation
    - GetNextAvailableSlotTests: Test slot availability logic
    - GenerateRecurringInstancesTests: Test recurring unavailability generation

Coverage: 95%+ for utility functions
Version: 2.2 (Recurring Unavailability)
"""
from datetime import datetime, time, date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from calendar_app.utils import (
    calculate_meeting_duration,
    format_time_slot,
    is_business_hours,
    get_next_available_slot,
    generate_recurring_instances
)
from calendar_app.models import Unavailability


class CalculateMeetingDurationTests(TestCase):
    """Test cases for calculate_meeting_duration function."""

    def test_duration_one_hour(self):
        """Test calculating duration for a 1-hour meeting."""
        start = time(9, 0)
        end = time(10, 0)
        self.assertEqual(calculate_meeting_duration(start, end), 60)

    def test_duration_thirty_minutes(self):
        """Test calculating duration for a 30-minute meeting."""
        start = time(14, 0)
        end = time(14, 30)
        self.assertEqual(calculate_meeting_duration(start, end), 30)

    def test_duration_two_hours(self):
        """Test calculating duration for a 2-hour meeting."""
        start = time(10, 0)
        end = time(12, 0)
        self.assertEqual(calculate_meeting_duration(start, end), 120)

    def test_duration_fifteen_minutes(self):
        """Test calculating duration for a 15-minute meeting."""
        start = time(9, 15)
        end = time(9, 30)
        self.assertEqual(calculate_meeting_duration(start, end), 15)

    def test_duration_with_minutes(self):
        """Test calculating duration with non-zero minutes."""
        start = time(9, 45)
        end = time(11, 15)
        self.assertEqual(calculate_meeting_duration(start, end), 90)


class FormatTimeSlotTests(TestCase):
    """Test cases for format_time_slot function."""

    def test_format_morning_time(self):
        """Test formatting morning time (AM)."""
        self.assertEqual(format_time_slot("09:00"), "9:00 AM")

    def test_format_afternoon_time(self):
        """Test formatting afternoon time (PM)."""
        self.assertEqual(format_time_slot("14:30"), "2:30 PM")

    def test_format_noon(self):
        """Test formatting noon (12:00 PM)."""
        self.assertEqual(format_time_slot("12:00"), "12:00 PM")

    def test_format_midnight(self):
        """Test formatting midnight (12:00 AM)."""
        self.assertEqual(format_time_slot("00:00"), "12:00 AM")

    def test_format_evening_time(self):
        """Test formatting evening time."""
        self.assertEqual(format_time_slot("18:45"), "6:45 PM")

    def test_format_early_morning(self):
        """Test formatting early morning time."""
        self.assertEqual(format_time_slot("01:30"), "1:30 AM")

    def test_format_with_leading_zeros(self):
        """Test formatting preserves minute leading zeros."""
        self.assertEqual(format_time_slot("09:05"), "9:05 AM")


class IsBusinessHoursTests(TestCase):
    """Test cases for is_business_hours function."""

    def test_start_of_business_hours(self):
        """Test that 8:00 AM is within business hours."""
        self.assertTrue(is_business_hours("08:00"))

    def test_end_of_business_hours(self):
        """Test that 7:59 PM is within business hours."""
        self.assertTrue(is_business_hours("19:59"))

    def test_just_after_business_hours(self):
        """Test that 8:00 PM is outside business hours."""
        self.assertFalse(is_business_hours("20:00"))

    def test_before_business_hours(self):
        """Test that 7:59 AM is outside business hours."""
        self.assertFalse(is_business_hours("07:59"))

    def test_mid_morning(self):
        """Test that 10:30 AM is within business hours."""
        self.assertTrue(is_business_hours("10:30"))

    def test_mid_afternoon(self):
        """Test that 3:00 PM is within business hours."""
        self.assertTrue(is_business_hours("15:00"))

    def test_early_morning(self):
        """Test that 6:00 AM is outside business hours."""
        self.assertFalse(is_business_hours("06:00"))

    def test_late_evening(self):
        """Test that 9:00 PM is outside business hours."""
        self.assertFalse(is_business_hours("21:00"))

    def test_midnight(self):
        """Test that midnight is outside business hours."""
        self.assertFalse(is_business_hours("00:00"))

    def test_noon(self):
        """Test that noon is within business hours."""
        self.assertTrue(is_business_hours("12:00"))


class GetNextAvailableSlotTests(TestCase):
    """Test cases for get_next_available_slot function."""

    def test_exact_slot_boundary(self):
        """Test time exactly on 30-minute boundary."""
        current = datetime(2025, 1, 1, 9, 0)
        result = get_next_available_slot(current, 30)
        self.assertEqual(result, "09:00")

    def test_round_up_to_next_slot(self):
        """Test time between slots rounds up."""
        current = datetime(2025, 1, 1, 9, 15)
        result = get_next_available_slot(current, 30)
        self.assertEqual(result, "09:30")

    def test_round_up_near_boundary(self):
        """Test time just after boundary rounds to next slot."""
        current = datetime(2025, 1, 1, 9, 1)
        result = get_next_available_slot(current, 30)
        self.assertEqual(result, "09:30")

    def test_round_up_just_before_boundary(self):
        """Test time just before boundary rounds to boundary."""
        current = datetime(2025, 1, 1, 9, 29)
        result = get_next_available_slot(current, 30)
        self.assertEqual(result, "09:30")

    def test_afternoon_slot(self):
        """Test afternoon time slot calculation."""
        current = datetime(2025, 1, 1, 14, 45)
        result = get_next_available_slot(current, 30)
        self.assertEqual(result, "15:00")

    def test_custom_slot_duration_15_min(self):
        """Test with 15-minute slot duration."""
        current = datetime(2025, 1, 1, 9, 10)
        result = get_next_available_slot(current, 15)
        self.assertEqual(result, "09:15")

    def test_custom_slot_duration_60_min(self):
        """Test with 60-minute slot duration."""
        current = datetime(2025, 1, 1, 9, 30)
        result = get_next_available_slot(current, 60)
        self.assertEqual(result, "10:00")

    def test_hour_boundary(self):
        """Test calculation across hour boundary."""
        current = datetime(2025, 1, 1, 9, 50)
        result = get_next_available_slot(current, 30)
        self.assertEqual(result, "10:00")

    def test_late_evening_slot(self):
        """Test late evening slot calculation."""
        current = datetime(2025, 1, 1, 19, 15)
        result = get_next_available_slot(current, 30)
        self.assertEqual(result, "19:30")



class GenerateRecurringInstancesTests(TestCase):
    """Test cases for generate_recurring_instances function."""

    def setUp(self):
        """Create test user and base recurring entry."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.start_date = date.today()

    def test_weekly_recurring_monday_wednesday_friday(self):
        """Test generating weekly recurring instances for MWF pattern."""
        # Create master recurring entry
        master = Unavailability.objects.create(
            user=self.user,
            date=self.start_date,
            start_time=time(9, 0),
            end_time=time(17, 0),
            description="Work hours",
            is_recurring=True,
            recurrence_pattern={
                "frequency": "weekly",
                "days": ["monday", "wednesday", "friday"],
                "interval": 1
            }
        )

        # Generate instances
        instances = generate_recurring_instances(master, days_ahead=14)

        # Should generate instances for MWF over next 2 weeks
        # Depending on start day, should be 4-6 instances
        self.assertGreaterEqual(len(instances), 3)
        self.assertLessEqual(len(instances), 6)

        # Verify all instances link to master
        for instance in instances:
            self.assertEqual(instance.parent_recurring_entry, master)
            self.assertFalse(instance.is_recurring)
            self.assertIsNone(instance.recurrence_pattern)
            self.assertEqual(instance.start_time, time(9, 0))
            self.assertEqual(instance.end_time, time(17, 0))

    def test_daily_recurring(self):
        """Test generating daily recurring instances."""
        master = Unavailability.objects.create(
            user=self.user,
            date=self.start_date,
            start_time=time(12, 0),
            end_time=time(13, 0),
            description="Lunch",
            is_recurring=True,
            recurrence_pattern={
                "frequency": "daily",
                "interval": 1
            }
        )

        instances = generate_recurring_instances(master, days_ahead=7)

        # Should generate 7 daily instances
        self.assertEqual(len(instances), 7)

    def test_monthly_recurring(self):
        """Test generating monthly recurring instances."""
        master = Unavailability.objects.create(
            user=self.user,
            date=date(2025, 1, 15),  # 15th of month
            start_time=time(9, 0),
            end_time=time(10, 0),
            description="Monthly meeting",
            is_recurring=True,
            recurrence_pattern={
                "frequency": "monthly",
                "interval": 1
            }
        )

        instances = generate_recurring_instances(master, days_ahead=90)

        # Should generate 2-3 monthly instances over 90 days
        self.assertGreaterEqual(len(instances), 2)
        self.assertLessEqual(len(instances), 3)

        # Verify all occur on 15th of month
        for instance in instances:
            self.assertEqual(instance.date.day, 15)

    def test_recurring_with_end_date(self):
        """Test recurring instances respect end_date."""
        end_date = (self.start_date + timedelta(days=20)).strftime("%Y-%m-%d")

        master = Unavailability.objects.create(
            user=self.user,
            date=self.start_date,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            recurrence_pattern={
                "frequency": "daily",
                "interval": 1,
                "end_date": end_date
            }
        )

        instances = generate_recurring_instances(master, days_ahead=90)

        # Should only generate 20 instances (respects end_date)
        self.assertEqual(len(instances), 20)

    def test_weekly_every_other_week(self):
        """Test weekly recurrence with interval=2 (biweekly)."""
        master = Unavailability.objects.create(
            user=self.user,
            date=self.start_date,
            start_time=time(14, 0),
            end_time=time(16, 0),
            is_recurring=True,
            recurrence_pattern={
                "frequency": "weekly",
                "days": ["monday"],
                "interval": 2  # Every other week
            }
        )

        instances = generate_recurring_instances(master, days_ahead=28)

        # Should generate 1-2 instances over 28 days (every 2 weeks)
        self.assertGreaterEqual(len(instances), 1)
        self.assertLessEqual(len(instances), 2)

    def test_not_recurring_raises_error(self):
        """Test that non-recurring entry raises ValueError."""
        non_recurring = Unavailability.objects.create(
            user=self.user,
            date=self.start_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_recurring=False
        )

        with self.assertRaises(ValueError) as context:
            generate_recurring_instances(non_recurring)

        self.assertIn("must be marked as recurring", str(context.exception))

    def test_no_pattern_raises_error(self):
        """Test that entry without pattern raises ValueError."""
        no_pattern = Unavailability.objects.create(
            user=self.user,
            date=self.start_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_recurring=True,
            recurrence_pattern=None
        )

        with self.assertRaises(ValueError) as context:
            generate_recurring_instances(no_pattern)

        self.assertIn("must have a recurrence_pattern", str(context.exception))

    def test_instances_exclude_start_date(self):
        """Test that generated instances do not include the start date."""
        master = Unavailability.objects.create(
            user=self.user,
            date=self.start_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_recurring=True,
            recurrence_pattern={
                "frequency": "daily",
                "interval": 1
            }
        )

        instances = generate_recurring_instances(master, days_ahead=7)

        # No instance should have the start_date
        instance_dates = [inst.date for inst in instances]
        self.assertNotIn(self.start_date, instance_dates)
