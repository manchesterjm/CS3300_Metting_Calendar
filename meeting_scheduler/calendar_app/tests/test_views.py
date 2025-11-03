"""
View tests for calendar_app

Tests for:
- CalendarView - personal calendar functionality
- HomeView - landing page for authenticated users

Covers GET/POST requests, form submissions, free time calculation, and user isolation.
"""
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from calendar_app.models import Unavailability


class CalendarViewTest(TestCase):
    """Tests for the calendar view"""

    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        self.url = reverse('calendar')
        # Create test user and login
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        # Create test unavailability entry
        Unavailability.objects.create(
            user=self.user,
            date=datetime.date(2025, 4, 15),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )

    def test_calendar_view_get(self):
        """Test GET request to calendar view"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/calendar.html')
        self.assertIn('form', response.context)
        self.assertIn('form_delete', response.context)

    def test_submit_unavailability(self):
        """Test submitting new unavailability"""
        post_data = {
            'date': '2025-05-01',
            'start_time': '09:00',
            'end_time': '10:00',
            'submit_unavailability': 'Submit'
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(
            Unavailability.objects.filter(
                date=datetime.date(2025, 5, 1),
                start_time=datetime.time(9, 0)
            ).exists()
        )

    def test_show_free_times(self):
        """Test showing free times for a date"""
        post_data = {
            'date': '2025-04-15',
            'start_time': '00:00',
            'end_time': '00:00',
            'show_free_times': 'Show'
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('free_times', response.context)
        self.assertIsNotNone(response.context['free_times'])

    def test_show_last_five(self):
        """Test showing last five entries"""
        # Create more entries
        for i in range(6):
            Unavailability.objects.create(
                user=self.user,
                date=datetime.date(2025, 5, i + 1),
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0)
            )
        post_data = {'show_last_five': 'Show'}
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form_delete'])
        # Should show only 5 most recent entries
        choices = response.context['form_delete'].fields['entry_ids'].choices
        self.assertLessEqual(len(choices), 5)

    def test_delete_selected(self):
        """Test deleting selected entries"""
        unavail = Unavailability.objects.create(
            user=self.user,
            date=datetime.date(2025, 5, 10),
            start_time=datetime.time(14, 0),
            end_time=datetime.time(15, 0)
        )
        post_data = {
            'entry_ids': [str(unavail.id)],
            'delete_selected': 'Delete'
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertFalse(Unavailability.objects.filter(id=unavail.id).exists())

    def test_free_times_calculation(self):
        """Test that free times are calculated correctly"""
        # Clear existing data
        Unavailability.objects.all().delete()
        # Create unavailability from 9:00 to 10:00
        Unavailability.objects.create(
            user=self.user,
            date=datetime.date(2025, 5, 1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )
        post_data = {
            'date': '2025-05-01',
            'start_time': '00:00',
            'end_time': '00:00',
            'show_free_times': 'Show'
        }
        response = self.client.post(self.url, post_data)
        free_times = response.context['free_times']
        # 9:00 and 9:30 should be taken
        self.assertNotIn('09:00', free_times)
        self.assertNotIn('09:30', free_times)
        # 8:00 and 10:00 should be free
        self.assertIn('08:00', free_times)
        self.assertIn('10:00', free_times)

    def test_30_minute_time_slots(self):
        """Test that time slots are exactly 30 minutes apart"""
        Unavailability.objects.all().delete()
        post_data = {
            'date': '2025-05-01',
            'start_time': '01:00',
            'end_time': '01:00',
            'show_free_times': 'Show'
        }
        response = self.client.post(self.url, post_data)
        free_times = response.context['free_times']
        # Check that we have 30-minute increments
        self.assertIn('08:00', free_times)
        self.assertIn('08:30', free_times)
        self.assertIn('09:00', free_times)
        self.assertIn('09:30', free_times)
        # Should NOT have 15-minute or 60-minute increments
        self.assertNotIn('08:15', free_times)
        self.assertNotIn('08:45', free_times)
        # Verify 30-minute spacing by checking consecutive slots
        if '08:00' in free_times:
            idx = free_times.index('08:00')
            if idx + 1 < len(free_times):
                self.assertEqual(free_times[idx + 1], '08:30')

    def test_time_range_boundaries(self):
        """Test that free times start at 8:00 and end before 20:00"""
        Unavailability.objects.all().delete()
        post_data = {
            'date': '2025-05-01',
            'start_time': '01:00',
            'end_time': '01:00',
            'show_free_times': 'Show'
        }
        response = self.client.post(self.url, post_data)
        free_times = response.context['free_times']
        # First slot should be 8:00
        self.assertEqual(free_times[0], '08:00')
        # Last slot should be 19:30 (not 20:00 or later)
        self.assertEqual(free_times[-1], '19:30')
        # Should not include 7:30 or 20:00
        self.assertNotIn('07:30', free_times)
        self.assertNotIn('20:00', free_times)
        self.assertNotIn('20:30', free_times)

    def test_last_five_exact_count(self):
        """Test that exactly 5 entries are shown, not more or less"""
        Unavailability.objects.all().delete()
        # Create exactly 7 entries
        for i in range(7):
            Unavailability.objects.create(
                user=self.user,
                date=datetime.date(2025, 5, i + 1),
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0)
            )
        post_data = {'show_last_five': 'Show'}
        response = self.client.post(self.url, post_data)
        choices = response.context['form_delete'].fields['entry_ids'].choices
        # Should show exactly 5, not 3 or 7
        self.assertEqual(len(choices), 5)

    def test_unavailability_exact_boundaries(self):
        """Test that unavailability marking uses correct boundary (< not <=)"""
        Unavailability.objects.all().delete()
        # Create unavailability from 9:00 to 9:30 exactly
        Unavailability.objects.create(
            user=self.user,
            date=datetime.date(2025, 5, 1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(9, 30)
        )
        post_data = {
            'date': '2025-05-01',
            'start_time': '01:00',
            'end_time': '01:00',
            'show_free_times': 'Show'
        }
        response = self.client.post(self.url, post_data)
        free_times = response.context['free_times']
        # 9:00 should be taken (start time)
        self.assertNotIn('09:00', free_times)
        # 9:30 should be FREE (end time is exclusive)
        self.assertIn('09:30', free_times)
        # 8:30 should be free (before start)
        self.assertIn('08:30', free_times)


class HomeViewTest(TestCase):
    """Tests for the home view"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()

    def test_home_view_requires_login(self):
        """Test that home view requires authentication"""
        response = self.client.get(reverse('home'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_home_view_authenticated(self):
        """Test that authenticated users can access home view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/home.html')

    def test_home_view_content(self):
        """Test that home view displays correct content"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        # Check for key elements that should be on the home page
        self.assertContains(response, 'Meeting Scheduler')
