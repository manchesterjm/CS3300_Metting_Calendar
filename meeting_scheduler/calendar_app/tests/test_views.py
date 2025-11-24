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


class JoinGroupViewTest(TestCase):
    """Tests for the join_group_view (join group via code)"""

    def setUp(self):
        """Set up test users and group"""
        self.user1 = User.objects.create_user(username='owner', password='pass123')
        self.user2 = User.objects.create_user(username='joiner', password='pass123')
        self.client = Client()

        from calendar_app.models import Group
        from calendar_app.utils import generate_join_code

        self.group = Group.objects.create(name='Test Group', created_by=self.user1)
        self.group.join_code = generate_join_code()
        self.group.join_code_enabled = True
        self.group.save()

    def test_join_group_get(self):
        """Test accessing join group page"""
        self.client.login(username='joiner', password='pass123')
        response = self.client.get(reverse('join_group'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/join_group.html')
        self.assertIn('form', response.context)

    def test_join_group_requires_login(self):
        """Test that join group view requires authentication"""
        response = self.client.get(reverse('join_group'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_join_group_valid_code(self):
        """Test joining group with valid code"""
        self.client.login(username='joiner', password='pass123')
        post_data = {'join_code': self.group.join_code}
        response = self.client.post(reverse('join_group'), post_data)

        # Should redirect to group detail
        self.assertEqual(response.status_code, 302)
        # User should now be a member
        self.assertTrue(self.group.is_member(self.user2))

    def test_join_group_invalid_code(self):
        """Test joining with invalid code returns generic error (prevents information disclosure)"""
        self.client.login(username='joiner', password='pass123')
        post_data = {'join_code': 'INVALID9'}
        response = self.client.post(reverse('join_group'), post_data)

        # Should show error, not redirect
        self.assertEqual(response.status_code, 200)
        # Security: Generic message prevents code enumeration
        self.assertContains(response, 'Invalid or inactive')
        self.assertFalse(self.group.is_member(self.user2))

    def test_join_group_disabled_code(self):
        """Test joining with disabled code returns generic error (prevents timing attacks)"""
        self.group.join_code_enabled = False
        self.group.save()

        self.client.login(username='joiner', password='pass123')
        post_data = {'join_code': self.group.join_code}
        response = self.client.post(reverse('join_group'), post_data)

        # Should show error
        self.assertEqual(response.status_code, 200)
        # Security: Generic message prevents information disclosure
        self.assertContains(response, 'Invalid or inactive')
        self.assertFalse(self.group.is_member(self.user2))

    def test_join_group_already_member(self):
        """Test joining when already a member returns generic error (prevents information disclosure)"""
        # Add user2 to group first
        self.group.members.add(self.user2)

        self.client.login(username='joiner', password='pass123')
        post_data = {'join_code': self.group.join_code}
        response = self.client.post(reverse('join_group'), post_data)

        # Should show error
        self.assertEqual(response.status_code, 200)
        # Security: Generic message prevents membership disclosure
        self.assertContains(response, 'Invalid or inactive')


class GenerateJoinCodeViewTest(TestCase):
    """Tests for the generate_join_code_view"""

    def setUp(self):
        """Set up test users and group"""
        self.owner = User.objects.create_user(username='owner', password='pass123')
        self.non_owner = User.objects.create_user(username='non_owner', password='pass123')
        self.client = Client()

        from calendar_app.models import Group
        self.group = Group.objects.create(name='Test Group', created_by=self.owner)

    def test_generate_code_requires_login(self):
        """Test that code generation requires authentication"""
        url = reverse('generate_join_code', args=[self.group.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_generate_code_owner_only(self):
        """Test that only owner can generate codes"""
        self.client.login(username='non_owner', password='pass123')
        url = reverse('generate_join_code', args=[self.group.id])
        response = self.client.post(url)

        # Should return 403 Forbidden (PermissionDenied)
        self.assertEqual(response.status_code, 403)

    def test_generate_code_success(self):
        """Test successful code generation"""
        self.client.login(username='owner', password='pass123')
        url = reverse('generate_join_code', args=[self.group.id])
        response = self.client.post(url)

        # Should redirect to group detail
        self.assertEqual(response.status_code, 302)

        # Refresh group from DB
        self.group.refresh_from_db()

        # Should have a join code now
        self.assertIsNotNone(self.group.join_code)
        self.assertEqual(len(self.group.join_code), 8)
        self.assertTrue(self.group.join_code_enabled)

    def test_generate_code_regeneration(self):
        """Test regenerating an existing code"""
        from calendar_app.utils import generate_join_code
        old_code = generate_join_code()
        self.group.join_code = old_code
        self.group.join_code_enabled = True
        self.group.save()

        self.client.login(username='owner', password='pass123')
        url = reverse('generate_join_code', args=[self.group.id])
        response = self.client.post(url)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Refresh group from DB
        self.group.refresh_from_db()

        # Should have a different code
        self.assertNotEqual(self.group.join_code, old_code)
        self.assertTrue(self.group.join_code_enabled)


class ToggleJoinCodeViewTest(TestCase):
    """Tests for the toggle_join_code_view"""

    def setUp(self):
        """Set up test users and group"""
        self.owner = User.objects.create_user(username='owner', password='pass123')
        self.non_owner = User.objects.create_user(username='non_owner', password='pass123')
        self.client = Client()

        from calendar_app.models import Group
        from calendar_app.utils import generate_join_code

        self.group = Group.objects.create(name='Test Group', created_by=self.owner)
        self.group.join_code = generate_join_code()
        self.group.join_code_enabled = True
        self.group.save()

    def test_toggle_requires_login(self):
        """Test that toggle requires authentication"""
        url = reverse('toggle_join_code', args=[self.group.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_toggle_owner_only(self):
        """Test that only owner can toggle codes"""
        self.client.login(username='non_owner', password='pass123')
        url = reverse('toggle_join_code', args=[self.group.id])
        response = self.client.post(url)

        # Should return 403 Forbidden (PermissionDenied)
        self.assertEqual(response.status_code, 403)

    def test_toggle_disable(self):
        """Test disabling an enabled code"""
        self.client.login(username='owner', password='pass123')
        url = reverse('toggle_join_code', args=[self.group.id])
        response = self.client.post(url)

        # Should redirect to group detail
        self.assertEqual(response.status_code, 302)

        # Refresh group from DB
        self.group.refresh_from_db()

        # Should be disabled now
        self.assertFalse(self.group.join_code_enabled)
        # Code should still exist
        self.assertIsNotNone(self.group.join_code)

    def test_toggle_enable(self):
        """Test enabling a disabled code"""
        self.group.join_code_enabled = False
        self.group.save()

        self.client.login(username='owner', password='pass123')
        url = reverse('toggle_join_code', args=[self.group.id])
        response = self.client.post(url)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Refresh group from DB
        self.group.refresh_from_db()

        # Should be enabled now
        self.assertTrue(self.group.join_code_enabled)

    def test_toggle_no_code_error(self):
        """Test toggling when no code exists"""
        self.group.join_code = None
        self.group.save()

        self.client.login(username='owner', password='pass123')
        url = reverse('toggle_join_code', args=[self.group.id])
        response = self.client.post(url)

        # Should redirect with error
        self.assertEqual(response.status_code, 302)
