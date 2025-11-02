"""
Unit tests for calendar utility functions.

This module contains comprehensive tests for the utility functions
used across the calendar application.
"""
from datetime import datetime, time
from django.test import TestCase
from calendar_app.utils import (
    calculate_meeting_duration,
    format_time_slot,
    is_business_hours,
    get_next_available_slot
)


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
