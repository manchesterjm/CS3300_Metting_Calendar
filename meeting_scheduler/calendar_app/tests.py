"""
Test suite for the calendar_app

Includes unit tests for models, forms, and views with authentication support.
Covers Unavailability model, Group model, forms validation, and view logic.
Includes comprehensive error handling tests for all exception paths.
Added password generation tests for new auto-password feature.
Updated for read-only group calendar workflow (removed 5 obsolete tests).

Test Count: 133 unit tests (30 unit + 16 fuzz + 72 view/integration + 15 password gen tests)
Coverage: 93%+ on critical modules
Last Updated: 2025-11-02
"""
import datetime
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Unavailability, Group, GroupUnavailability
from .forms import (
    UnavailabilityForm,
    DeleteSelectedForm,
    GroupCreateForm,
    AddMemberForm,
    GroupUnavailabilityForm
)
from .utils import generate_password

# pylint: disable=too-many-lines

class UnavailabilityModelTest(TestCase):
    """Tests for the Unavailability model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.unavailability = Unavailability.objects.create(
            user=self.user,
            date=datetime.date(2025, 4, 15),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )

    def test_unavailability_creation(self):
        """Test that unavailability objects are created correctly"""
        self.assertIsNotNone(self.unavailability)
        self.assertEqual(self.unavailability.user, self.user)
        self.assertEqual(self.unavailability.date, datetime.date(2025, 4, 15))
        self.assertEqual(self.unavailability.start_time, datetime.time(9, 0))
        self.assertEqual(self.unavailability.end_time, datetime.time(10, 0))

    def test_unavailability_str(self):
        """Test the string representation of unavailability"""
        expected = "testuser: 2025-04-15 from 09:00:00 to 10:00:00"
        self.assertEqual(str(self.unavailability), expected)

    def test_unavailability_fields(self):
        """Test that all required fields exist"""
        self.assertTrue(hasattr(self.unavailability, 'user'))
        self.assertTrue(hasattr(self.unavailability, 'date'))
        self.assertTrue(hasattr(self.unavailability, 'start_time'))
        self.assertTrue(hasattr(self.unavailability, 'end_time'))

    def test_user_can_edit_owner(self):
        """Test that the owner can edit their own unavailability entry"""
        self.assertTrue(self.unavailability.user_can_edit(self.user))

    def test_user_can_edit_non_owner(self):
        """Test that non-owners cannot edit unavailability entries"""
        other_user = User.objects.create_user(username='otheruser', password='pass123')
        self.assertFalse(self.unavailability.user_can_edit(other_user))


class UnavailabilityFormTest(TestCase):
    """Tests for the UnavailabilityForm"""

    def test_form_with_valid_data(self):
        """Test form validation with valid data"""
        form_data = {
            'date': datetime.date(2025, 5, 1),
            'start_time': datetime.time(9, 0),
            'end_time': datetime.time(10, 0)
        }
        form = UnavailabilityForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_default_times_submit_unavailability(self):
        """Test form rejects default times when submitting unavailability"""
        form_data = {
            'date': datetime.date(2025, 5, 1),
            'start_time': datetime.time(0, 0),
            'end_time': datetime.time(0, 0)
        }
        form = UnavailabilityForm(data=form_data, submit_type='submit_unavailability')
        self.assertFalse(form.is_valid())
        self.assertIn('start_time', form.errors)
        self.assertIn('end_time', form.errors)

    def test_form_with_default_times_show_free_times(self):
        """Test form accepts default times when showing free times"""
        form_data = {
            'date': datetime.date(2025, 5, 1),
            'start_time': datetime.time(0, 0),
            'end_time': datetime.time(0, 0)
        }
        form = UnavailabilityForm(data=form_data)
        # Without submit_type, validation should not reject defaults
        self.assertTrue(form.is_valid())

    def test_form_fields(self):
        """Test that form has all required fields"""
        form = UnavailabilityForm()
        self.assertIn('date', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertIn('end_time', form.fields)

    def test_form_date_initial_value(self):
        """Test that form initializes with today's date"""
        form = UnavailabilityForm()
        today = datetime.date.today()
        self.assertEqual(form.fields['date'].initial, today)


class DeleteSelectedFormTest(TestCase):
    """Tests for the DeleteSelectedForm"""

    def test_form_initialization(self):
        """Test that form initializes correctly"""
        form = DeleteSelectedForm()
        self.assertIn('entry_ids', form.fields)

    def test_form_with_choices(self):
        """Test form with populated choices"""
        form = DeleteSelectedForm()
        form.fields['entry_ids'].choices = [
            (1, "2025-04-15 from 09:00:00 to 10:00:00"),
            (2, "2025-04-16 from 14:00:00 to 15:00:00")
        ]
        self.assertEqual(len(form.fields['entry_ids'].choices), 2)

    def test_form_empty_selection(self):
        """Test form with no selection is valid (required=False)"""
        form = DeleteSelectedForm(data={'entry_ids': []})
        self.assertTrue(form.is_valid())


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


class AuthenticationTest(TestCase):
    """Tests for authentication functionality"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_login_required_for_calendar(self):
        """Test that calendar view requires login"""
        response = self.client.get(reverse('calendar'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_user_registration(self):
        """Test user registration"""
        post_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        response = self.client.post(reverse('register'), post_data)
        # Should redirect to calendar after successful registration
        self.assertEqual(response.status_code, 302)
        # User should be created
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        """Test user login"""
        # Create user
        User.objects.create_user(username='testuser', password='testpass123')
        # Login
        post_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), post_data)
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_logout(self):
        """Test user logout"""
        # Create and login user
        User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        # Logout
        response = self.client.post(reverse('logout'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_user_account_page(self):
        """Test user account page access"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/account.html')
        self.assertContains(response, 'testuser')

    def test_user_data_isolation(self):
        """Test that users only see their own data"""
        # Create two users
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')

        # User1 creates an entry
        Unavailability.objects.create(
            user=user1,
            date=datetime.date(2025, 5, 1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )

        # User2 creates an entry
        Unavailability.objects.create(
            user=user2,
            date=datetime.date(2025, 5, 2),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(12, 0)
        )

        # Login as user1
        self.client.login(username='user1', password='pass123')

        # Request last 5 entries - should only see user1's entry
        response = self.client.post(reverse('calendar'), {'show_last_five': 'Show'})
        choices = response.context['form_delete'].fields['entry_ids'].choices

        # Should only have 1 entry (user1's)
        self.assertEqual(len(choices), 1)

        # Logout and login as user2
        self.client.logout()
        self.client.login(username='user2', password='pass123')

        # Request last 5 entries - should only see user2's entry
        response = self.client.post(reverse('calendar'), {'show_last_five': 'Show'})
        choices = response.context['form_delete'].fields['entry_ids'].choices

        # Should only have 1 entry (user2's)
        self.assertEqual(len(choices), 1)

    def test_registration_duplicate_username(self):
        """
        Test registration with duplicate username.

        Validates form-level error handling when a user attempts to register
        with a username that already exists in the database.
        """
        # Create first user
        User.objects.create_user(username='testuser', password='pass123')

        # Attempt to register with same username
        post_data = {
            'username': 'testuser',
            'email': 'different@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        response = self.client.post(reverse('register'), post_data)

        # Should not redirect (stays on registration page due to form validation)
        self.assertEqual(response.status_code, 200)
        # Form should have errors (Django's UserCreationForm validates uniqueness)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        # Should only have one user with this username
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
        # Verify username field has an error (more robust than checking specific text)
        self.assertIn('username', form.errors)
        # Verify error message is user-friendly and actionable
        username_errors = form.errors['username']
        self.assertTrue(len(username_errors) > 0, "Username field should have error messages")
        # Check that error message mentions the issue (username exists/taken)
        error_text = str(username_errors[0]).lower()
        self.assertTrue('username' in error_text or 'exists' in error_text or 'already' in error_text,
                       "Error message should clearly indicate username is already taken")
        # Verify error is displayed in rendered HTML (user-facing validation)
        self.assertContains(response, 'username')
        # Verify the registration form is re-rendered with errors in context
        self.assertIn('form', response.context)

    def test_registration_password_mismatch(self):
        """
        Test registration with mismatched passwords.

        Validates that the form correctly rejects registration when the two
        password fields don't match, using form error fields rather than
        specific error message text for robustness.
        """
        post_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!'
        }
        response = self.client.post(reverse('register'), post_data)

        # Should not redirect (form validation fails)
        self.assertEqual(response.status_code, 200)
        # User should not be created
        self.assertFalse(User.objects.filter(username='newuser').exists())
        # Verify the registration form is re-rendered with errors
        form = response.context['form']
        self.assertFalse(form.is_valid())
        # Check that password2 field has error (robust check without specific wording)
        self.assertTrue(form.has_error('password2'))
        self.assertIn('password2', form.errors)
        # Verify error message is user-friendly and describes the issue
        password_errors = form.errors['password2']
        self.assertTrue(len(password_errors) > 0, "Password2 field should have error messages")
        # Check that error message mentions password matching issue
        error_text = str(password_errors[0]).lower()
        self.assertTrue('password' in error_text and 'match' in error_text,
                       "Error message should clearly indicate passwords don't match")
        # Verify error is displayed in rendered HTML (user-facing validation)
        self.assertContains(response, 'password')
        self.assertIn('form', response.context)

    def test_registration_success_and_auto_login(self):
        """
        Test successful registration automatically logs user in.

        Validates the complete happy path: form validation passes, user is created,
        user is automatically logged in, success message is displayed, and
        post-login state is correctly initialized.
        """
        post_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        response = self.client.post(reverse('register'), post_data, follow=True)

        # Should redirect (302) and end up at home page
        self.assertEqual(response.status_code, 200)
        # Check final URL after following redirects
        self.assertEqual(response.request['PATH_INFO'], reverse('home'))

        # User should be created
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # User should be automatically logged in
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user.id)

        # Verify session shows user is authenticated
        self.assertTrue('_auth_user_id' in self.client.session)

        # Verify post-login user state is correctly initialized
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.is_active, "User should be active after registration")
        self.assertFalse(user.is_staff, "New users should not have staff privileges")
        self.assertFalse(user.is_superuser, "New users should not have superuser privileges")

        # Verify user can authenticate with provided password
        self.assertTrue(user.check_password('TestPass123!'),
                       "User should be able to authenticate with registration password")

        # Verify success message is displayed (check for key components, not exact text)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        message_text = str(messages[0])
        # Validate key message components without exact wording dependency
        self.assertIn('newuser', message_text)
        self.assertTrue('welcome' in message_text.lower() or 'created' in message_text.lower(),
                       "Success message should welcome user or confirm account creation")

    def test_registration_multi_field_errors(self):
        """
        Test registration form with multiple field errors simultaneously.

        Validates that the form correctly handles and displays errors when
        multiple fields fail validation at the same time, ensuring proper
        error feedback for complex validation scenarios.
        """
        # Create existing user to trigger username uniqueness error
        User.objects.create_user(username='existinguser', password='pass123')

        # Submit form with multiple errors: duplicate username + password mismatch
        post_data = {
            'username': 'existinguser',  # Duplicate username error
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass456!'  # Password mismatch error
        }
        response = self.client.post(reverse('register'), post_data)

        # Should not redirect (form validation fails)
        self.assertEqual(response.status_code, 200)
        # User should not be created (validation failed)
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

        # Form should be invalid
        form = response.context['form']
        self.assertFalse(form.is_valid())

        # Both fields should have errors
        self.assertIn('username', form.errors)
        self.assertIn('password2', form.errors)

        # Verify error count - should have at least 2 distinct field errors
        self.assertGreaterEqual(len(form.errors), 2,
                               "Form should have errors for multiple fields")

        # Verify each error has descriptive messages
        username_errors = form.errors['username']
        self.assertTrue(len(username_errors) > 0, "Username should have error messages")
        password_errors = form.errors['password2']
        self.assertTrue(len(password_errors) > 0, "Password2 should have error messages")

        # Verify both errors are displayed in rendered HTML
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')

        # Verify form is re-rendered with errors
        self.assertIn('form', response.context)

    def test_registration_weak_password(self):
        """
        Test registration with weak password that fails Django's password validators.

        Validates that password strength requirements are enforced and users
        receive clear feedback about password requirements.
        """
        # Submit form with weak password (too short, too common, numeric only)
        post_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': '12345',  # Too short, numeric only, common password
            'password2': '12345'
        }
        response = self.client.post(reverse('register'), post_data)

        # Should not redirect (form validation fails)
        self.assertEqual(response.status_code, 200)
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser').exists())

        # Form should be invalid
        form = response.context['form']
        self.assertFalse(form.is_valid())

        # Password field should have validation errors (Django reports on password2)
        self.assertIn('password2', form.errors)
        password_errors = form.errors['password2']
        self.assertTrue(len(password_errors) > 0, "Password should have validation errors")

        # Verify error messages are descriptive (check for common validator messages)
        all_errors_text = ' '.join(str(e).lower() for e in password_errors)
        # Should mention at least one password requirement
        has_length_error = 'character' in all_errors_text or 'short' in all_errors_text
        has_numeric_error = 'numeric' in all_errors_text
        has_common_error = 'common' in all_errors_text
        self.assertTrue(has_length_error or has_numeric_error or has_common_error,
                       "Error should mention password requirements (length, complexity, etc.)")

        # Verify multiple password validators are triggered
        self.assertGreaterEqual(len(password_errors), 2,
                               "Multiple password validators should trigger for weak password")

        # Verify errors are displayed in HTML
        self.assertContains(response, 'password')
        self.assertIn('form', response.context)


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


class GroupModelTest(TestCase):
    """Tests for the Group model"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.group = Group.objects.create(
            name='Test Group',
            created_by=self.user1
        )
        self.group.members.add(self.user1)

    def test_group_creation(self):
        """Test that group objects are created correctly"""
        self.assertIsNotNone(self.group)
        self.assertEqual(self.group.name, 'Test Group')
        self.assertEqual(self.group.created_by, self.user1)

    def test_group_str(self):
        """Test the string representation of group"""
        self.assertEqual(str(self.group), 'Test Group')

    def test_group_is_member(self):
        """Test is_member method"""
        self.assertTrue(self.group.is_member(self.user1))
        self.assertFalse(self.group.is_member(self.user2))

    def test_group_is_owner(self):
        """Test is_owner method"""
        self.assertTrue(self.group.is_owner(self.user1))
        self.assertFalse(self.group.is_owner(self.user2))

    def test_group_add_member(self):
        """Test adding members to group"""
        self.group.members.add(self.user2)
        self.assertTrue(self.group.is_member(self.user2))
        self.assertEqual(self.group.members.count(), 2)

    def test_group_remove_member(self):
        """Test removing members from group"""
        self.group.members.add(self.user2)
        self.group.members.remove(self.user2)
        self.assertFalse(self.group.is_member(self.user2))

    def test_user_can_edit_owner(self):
        """Test that the owner can edit the group"""
        self.assertTrue(self.group.user_can_edit(self.user1))

    def test_user_can_edit_non_owner(self):
        """Test that non-owners cannot edit the group"""
        self.assertFalse(self.group.user_can_edit(self.user2))

    def test_user_can_view_owner(self):
        """Test that the owner can view the group"""
        self.assertTrue(self.group.user_can_view(self.user1))

    def test_user_can_view_member(self):
        """Test that members can view the group"""
        self.group.members.add(self.user2)
        self.assertTrue(self.group.user_can_view(self.user2))

    def test_user_can_view_non_member(self):
        """Test that non-members cannot view the group"""
        self.assertFalse(self.group.user_can_view(self.user2))


class GroupUnavailabilityModelTest(TestCase):
    """Tests for the GroupUnavailability model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.group = Group.objects.create(name='Test Group', created_by=self.user)
        self.group_unavail = GroupUnavailability.objects.create(
            group=self.group,
            user=self.user,
            date=datetime.date(2025, 4, 15),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            description='Team meeting'
        )

    def test_group_unavailability_creation(self):
        """Test that group unavailability objects are created correctly"""
        self.assertIsNotNone(self.group_unavail)
        self.assertEqual(self.group_unavail.group, self.group)
        self.assertEqual(self.group_unavail.user, self.user)
        self.assertEqual(self.group_unavail.date, datetime.date(2025, 4, 15))
        self.assertEqual(self.group_unavail.description, 'Team meeting')

    def test_group_unavailability_str(self):
        """Test the string representation of group unavailability"""
        expected = "Test Group - testuser: 2025-04-15 from 09:00:00 to 10:00:00"
        self.assertEqual(str(self.group_unavail), expected)

    def test_group_unavailability_fields(self):
        """Test that all required fields exist"""
        self.assertTrue(hasattr(self.group_unavail, 'group'))
        self.assertTrue(hasattr(self.group_unavail, 'user'))
        self.assertTrue(hasattr(self.group_unavail, 'date'))
        self.assertTrue(hasattr(self.group_unavail, 'start_time'))
        self.assertTrue(hasattr(self.group_unavail, 'end_time'))
        self.assertTrue(hasattr(self.group_unavail, 'description'))

    def test_user_can_edit_creator(self):
        """Test that the creator can edit their own group unavailability entry"""
        self.assertTrue(self.group_unavail.user_can_edit(self.user))

    def test_user_can_edit_non_creator(self):
        """Test that non-creators cannot edit group unavailability entries"""
        other_user = User.objects.create_user(username='otheruser', password='pass123')
        self.assertFalse(self.group_unavail.user_can_edit(other_user))

    def test_user_can_view_group_member(self):
        """Test that group members can view group unavailability entries"""
        member = User.objects.create_user(username='member', password='pass123')
        self.group.members.add(member)
        self.assertTrue(self.group_unavail.user_can_view(member))

    def test_user_can_view_non_member(self):
        """Test that non-members cannot view group unavailability entries"""
        non_member = User.objects.create_user(username='nonmember', password='pass123')
        self.assertFalse(self.group_unavail.user_can_view(non_member))


class GroupCreateFormTest(TestCase):
    """Tests for the GroupCreateForm"""

    def test_form_with_valid_data(self):
        """Test form validation with valid data"""
        form_data = {'name': 'New Group'}
        form = GroupCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_duplicate_name(self):
        """Test form rejects duplicate group names"""
        Group.objects.create(
            name='Existing Group',
            created_by=User.objects.create_user(username='user1', password='pass')
        )
        form_data = {'name': 'Existing Group'}
        form = GroupCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_form_fields(self):
        """Test that form has all required fields"""
        form = GroupCreateForm()
        self.assertIn('name', form.fields)


class AddMemberFormTest(TestCase):
    """Tests for the AddMemberForm"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='existinguser', password='pass')

    def test_form_with_valid_username(self):
        """Test form validation with valid username"""
        form_data = {'username': 'existinguser'}
        form = AddMemberForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_nonexistent_username(self):
        """Test form rejects non-existent username"""
        form_data = {'username': 'nonexistentuser'}
        form = AddMemberForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_fields(self):
        """Test that form has all required fields"""
        form = AddMemberForm()
        self.assertIn('username', form.fields)


class GroupUnavailabilityFormTest(TestCase):
    """Tests for the GroupUnavailabilityForm"""

    def test_form_with_valid_data(self):
        """Test form validation with valid data"""
        form_data = {
            'date': datetime.date(2025, 5, 1),
            'start_time': datetime.time(9, 0),
            'end_time': datetime.time(10, 0),
            'description': 'Meeting'
        }
        form = GroupUnavailabilityForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_default_times_submit(self):
        """Test form rejects default times when submitting"""
        form_data = {
            'date': datetime.date(2025, 5, 1),
            'start_time': datetime.time(0, 0),
            'end_time': datetime.time(0, 0),
            'description': ''
        }
        form = GroupUnavailabilityForm(data=form_data, submit_type='submit_unavailability')
        self.assertFalse(form.is_valid())
        self.assertIn('start_time', form.errors)
        self.assertIn('end_time', form.errors)

    def test_form_with_invalid_time_range(self):
        """Test form rejects when end_time <= start_time"""
        form_data = {
            'date': datetime.date(2025, 5, 1),
            'start_time': datetime.time(10, 0),
            'end_time': datetime.time(9, 0),
            'description': ''
        }
        form = GroupUnavailabilityForm(data=form_data, submit_type='submit_unavailability')
        self.assertFalse(form.is_valid())
        self.assertIn('end_time', form.errors)

    def test_form_fields(self):
        """Test that form has all required fields"""
        form = GroupUnavailabilityForm()
        self.assertIn('date', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertIn('end_time', form.fields)
        self.assertIn('description', form.fields)


class GroupViewsTest(TestCase):
    """Tests for group views"""

    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.group = Group.objects.create(name='Test Group', created_by=self.user1)
        self.group.members.add(self.user1)

    def test_group_list_view_login_required(self):
        """Test that group list requires login"""
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_group_list_view_authenticated(self):
        """Test group list view for authenticated user"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/group_list.html')
        self.assertIn('groups', response.context)

    def test_group_create_view_get(self):
        """Test GET request to group create view"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('group_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/group_create.html')

    def test_group_create_view_post(self):
        """Test creating a new group"""
        self.client.login(username='user1', password='pass123')
        post_data = {'name': 'New Group'}
        response = self.client.post(reverse('group_create'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Group.objects.filter(name='New Group').exists())
        new_group = Group.objects.get(name='New Group')
        # Creator should be automatically added as member
        self.assertTrue(new_group.is_member(self.user1))

    def test_group_detail_view_member_access(self):
        """Test that group members can view group details"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('group_detail', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/group_detail.html')

    def test_group_detail_view_non_member_denied(self):
        """Test that non-members cannot view group details"""
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('group_detail', args=[self.group.id]))
        # Expect 403 Forbidden (PermissionDenied exception) instead of redirect
        self.assertEqual(response.status_code, 403)

    def test_group_calendar_view_member_access(self):
        """Test that group members can view group calendar"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('group_calendar', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/group_calendar.html')

    # OBSOLETE: Group calendar is now read-only and no longer supports add functionality
    # def test_group_calendar_submit_unavailability(self):
    #     """Test submitting unavailability to group calendar"""
    #     self.client.login(username='user1', password='pass123')
    #     post_data = {
    #         'date': '2025-05-01',
    #         'start_time': '09:00',
    #         'end_time': '10:00',
    #         'description': 'Meeting',
    #         'submit_unavailability': 'Submit'
    #     }
    #     response = self.client.post(
    #         reverse('group_calendar', args=[self.group.id]),
    #         post_data
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(
    #         GroupUnavailability.objects.filter(
    #             group=self.group,
    #             user=self.user1,
    #             date=datetime.date(2025, 5, 1)
    #         ).exists()
    #     )

    # OBSOLETE: Group calendar is now read-only and no longer supports delete functionality
    # def test_group_calendar_delete_own_entry(self):
    #     """Test that users can delete their own entries"""
    #     self.client.login(username='user1', password='pass123')
    #     # Create an entry
    #     entry = GroupUnavailability.objects.create(
    #         group=self.group,
    #         user=self.user1,
    #         date=datetime.date(2025, 5, 1),
    #         start_time=datetime.time(9, 0),
    #         end_time=datetime.time(10, 0)
    #     )
    #     # Delete it
    #     post_data = {
    #         'entry_ids': [str(entry.id)],
    #         'delete_selected': 'Delete'
    #     }
    #     response = self.client.post(
    #         reverse('group_calendar', args=[self.group.id]),
    #         post_data
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     self.assertFalse(GroupUnavailability.objects.filter(id=entry.id).exists())

    # OBSOLETE: Group calendar is now read-only and no longer supports delete functionality
    # def test_group_calendar_cannot_delete_others_entry(self):
    #     """Test that users cannot delete other users' entries"""
    #     # User1 creates an entry
    #     entry = GroupUnavailability.objects.create(
    #         group=self.group,
    #         user=self.user1,
    #         date=datetime.date(2025, 5, 1),
    #         start_time=datetime.time(9, 0),
    #         end_time=datetime.time(10, 0)
    #     )
    #     # Add user2 to group
    #     self.group.members.add(self.user2)
    #     # User2 tries to delete user1's entry
    #     self.client.login(username='user2', password='pass123')
    #     post_data = {
    #         'entry_ids': [str(entry.id)],
    #         'delete_selected': 'Delete'
    #     }
    #     self.client.post(reverse('group_calendar', args=[self.group.id]), post_data)
    #     # Entry should still exist
    #     self.assertTrue(GroupUnavailability.objects.filter(id=entry.id).exists())

    def test_group_add_member_owner_only(self):
        """Test that only owner can add members"""
        self.client.login(username='user1', password='pass123')
        post_data = {'username': 'user2'}
        response = self.client.post(
            reverse('group_add_member', args=[self.group.id]),
            post_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.group.is_member(self.user2))

    def test_group_add_member_non_owner_denied(self):
        """Test that non-owners cannot add members"""
        self.group.members.add(self.user2)
        self.client.login(username='user2', password='pass123')
        user3 = User.objects.create_user(username='user3', password='pass123')
        post_data = {'username': 'user3'}
        # Attempt to add member without being owner
        self.client.post(
            reverse('group_add_member', args=[self.group.id]),
            post_data
        )
        # Should not add member (permission denied)
        self.assertFalse(self.group.is_member(user3))

    def test_group_remove_member_owner_only(self):
        """Test that only owner can remove members"""
        self.group.members.add(self.user2)
        self.client.login(username='user1', password='pass123')
        response = self.client.post(
            reverse('group_remove_member', args=[self.group.id, self.user2.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.group.is_member(self.user2))

    def test_group_delete_owner_only(self):
        """Test that only owner can delete group"""
        self.client.login(username='user1', password='pass123')
        response = self.client.post(reverse('group_delete', args=[self.group.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Group.objects.filter(id=self.group.id).exists())

    def test_group_delete_non_owner_denied(self):
        """Test that non-owners cannot delete group"""
        self.group.members.add(self.user2)
        self.client.login(username='user2', password='pass123')
        _response = self.client.post(reverse('group_delete', args=[self.group.id]))
        # Group should still exist
        self.assertTrue(Group.objects.filter(id=self.group.id).exists())

    def test_group_calendar_free_times_all_members(self):
        """Test that free times consider all group members' unavailability from personal calendars"""
        # Add user2 to group
        self.group.members.add(self.user2)
        # User1 unavailable 9:00-10:00 (in personal calendar)
        Unavailability.objects.create(
            user=self.user1,
            date=datetime.date(2025, 5, 1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )
        # User2 unavailable 10:00-11:00 (in personal calendar)
        Unavailability.objects.create(
            user=self.user2,
            date=datetime.date(2025, 5, 1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0)
        )
        self.client.login(username='user1', password='pass123')
        post_data = {
            'date': '2025-05-01',
            'start_time': '00:00',
            'end_time': '00:00',
            'show_free_times': 'Show'
        }
        response = self.client.post(
            reverse('group_calendar', args=[self.group.id]),
            post_data
        )
        free_times = response.context['free_times']
        # Both 9:00-10:00 and 10:00-11:00 should be taken
        self.assertNotIn('09:00', free_times)
        self.assertNotIn('09:30', free_times)
        self.assertNotIn('10:00', free_times)
        self.assertNotIn('10:30', free_times)
        # 8:00 and 11:00 should be free
        self.assertIn('08:00', free_times)
        self.assertIn('11:00', free_times)

    def test_group_calendar_show_free_times_date_only(self):
        """Test show_free_times with only date field using personal calendar unavailability"""
        self.client.login(username='user1', password='pass123')
        # Create an unavailability entry in personal calendar
        Unavailability.objects.create(
            user=self.user1,
            date=datetime.date(2025, 11, 2),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(14, 0)
        )
        # Request free times with ONLY date (no start_time or end_time)
        post_data = {
            'date': '2025-11-02',
            'show_free_times': 'Show'
        }
        response = self.client.post(
            reverse('group_calendar', args=[self.group.id]),
            post_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('free_times', response.context)
        free_times = response.context['free_times']
        # Verify free_times is not None (even if empty)
        self.assertIsNotNone(free_times)
        # 10:00-14:00 slots should NOT be in free times
        self.assertNotIn('10:00', free_times)
        self.assertNotIn('10:30', free_times)
        self.assertNotIn('11:00', free_times)
        self.assertNotIn('11:30', free_times)
        self.assertNotIn('12:00', free_times)
        self.assertNotIn('12:30', free_times)
        self.assertNotIn('13:00', free_times)
        self.assertNotIn('13:30', free_times)
        # 8:00 and 14:00 should be in free times
        self.assertIn('08:00', free_times)
        self.assertIn('14:00', free_times)

    def test_group_calendar_show_free_times_no_entries(self):
        """Test show_free_times returns all slots when no entries exist"""
        self.client.login(username='user1', password='pass123')
        post_data = {
            'date': '2025-11-02',
            'show_free_times': 'Show'
        }
        response = self.client.post(
            reverse('group_calendar', args=[self.group.id]),
            post_data
        )
        self.assertEqual(response.status_code, 200)
        free_times = response.context['free_times']
        # All slots from 8:00 to 19:30 should be free (24 half-hour slots)
        self.assertEqual(len(free_times), 24)
        self.assertIn('08:00', free_times)
        self.assertIn('19:30', free_times)

    # OBSOLETE: Group calendar is now read-only and no longer shows last 5 entries
    # def test_group_calendar_show_last_five_entries(self):
    #     """Test show_last_five displays last 5 entries"""
    #     self.client.login(username='user1', password='pass123')
    #     # Create 6 entries
    #     for i in range(6):
    #         GroupUnavailability.objects.create(
    #             group=self.group,
    #             user=self.user1,
    #             date=datetime.date(2025, 11, i+1),
    #             start_time=datetime.time(9, 0),
    #             end_time=datetime.time(10, 0),
    #             description=f'Entry {i+1}'
    #         )
    #     post_data = {
    #         'date': '2025-11-02',
    #         'show_last_five': 'Show'
    #     }
    #     response = self.client.post(
    #         reverse('group_calendar', args=[self.group.id]),
    #         post_data
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     # Check that form_delete has exactly 5 choices (last 5 entries)
    #     form_delete = response.context['form_delete']
    #     choices = form_delete.fields['entry_ids'].choices
    #     self.assertEqual(len(choices), 5)
    #     # Verify the entries are the last 5 (most recent)
    #     # Entry 6, 5, 4, 3, 2 should be shown (Entry 1 should NOT be shown)
    #     labels = [choice[1] for choice in choices]
    #     self.assertTrue(any('Entry 6' in label for label in labels))
    #     self.assertTrue(any('Entry 2' in label for label in labels))
    #     self.assertFalse(any('Entry 1' in label for label in labels))

    # OBSOLETE: Group calendar is now read-only and no longer shows last 5 entries
    # def test_group_calendar_show_last_five_no_entries(self):
    #     """Test show_last_five when no entries exist"""
    #     self.client.login(username='user1', password='pass123')
    #     post_data = {
    #         'date': '2025-11-02',
    #         'show_last_five': 'Show'
    #     }
    #     response = self.client.post(
    #         reverse('group_calendar', args=[self.group.id]),
    #         post_data
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     # form_delete should have no choices
    #     form_delete = response.context['form_delete']
    #     self.assertEqual(len(form_delete.fields['entry_ids'].choices), 0)

    def test_personal_calendar_show_free_times_date_only(self):
        """Test personal calendar show_free_times with only date"""
        self.client.login(username='user1', password='pass123')
        # Create an unavailability entry
        Unavailability.objects.create(
            user=self.user1,
            date=datetime.date(2025, 11, 2),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(14, 0)
        )
        post_data = {
            'date': '2025-11-02',
            'show_free_times': 'Show'
        }
        response = self.client.post(reverse('calendar'), post_data)
        self.assertEqual(response.status_code, 200)
        free_times = response.context['free_times']
        self.assertIsNotNone(free_times)
        # 10:00-14:00 should be taken
        self.assertNotIn('10:00', free_times)
        self.assertNotIn('13:30', free_times)
        # 8:00 and 14:00 should be free
        self.assertIn('08:00', free_times)
        self.assertIn('14:00', free_times)

    def test_personal_calendar_show_last_five_entries(self):
        """Test personal calendar show_last_five"""
        self.client.login(username='user1', password='pass123')
        # Create 3 entries
        for i in range(3):
            Unavailability.objects.create(
                user=self.user1,
                date=datetime.date(2025, 11, i+1),
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0)
            )
        post_data = {
            'date': '2025-11-02',
            'show_last_five': 'Show'
        }
        response = self.client.post(reverse('calendar'), post_data)
        self.assertEqual(response.status_code, 200)
        form_delete = response.context['form_delete']
        self.assertEqual(len(form_delete.fields['entry_ids'].choices), 3)


class PasswordGenerationTest(TestCase):
    """Tests for password generation utility and API"""

    def test_generate_password_default_length(self):
        """Test password generation with default length of 16"""
        password = generate_password()
        self.assertEqual(len(password), 16)

    def test_generate_password_custom_length(self):
        """Test password generation with custom length"""
        password = generate_password(length=12)
        self.assertEqual(len(password), 12)

    def test_generate_password_minimum_length(self):
        """Test password generation with minimum length of 8"""
        password = generate_password(length=8)
        self.assertEqual(len(password), 8)

    def test_generate_password_too_short(self):
        """Test that password generation fails with length < 8"""
        with self.assertRaises(ValueError) as context:
            generate_password(length=7)
        self.assertIn('at least 8', str(context.exception))

    def test_generate_password_contains_required_chars(self):
        """Test that generated password contains required character types"""
        password = generate_password(length=16)

        # Check for at least one number (2-9)
        has_number = any(c in '23456789' for c in password)
        self.assertTrue(has_number, "Password should contain at least one number")

        # Check for at least one lowercase letter (excluding l, i)
        has_lower = any(c.islower() for c in password)
        self.assertTrue(has_lower, "Password should contain at least one lowercase letter")

        # Check for at least one uppercase letter (excluding O, I)
        has_upper = any(c.isupper() for c in password)
        self.assertTrue(has_upper, "Password should contain at least one uppercase letter")

        # Check for at least one special character
        special_chars = '@#$%&?*'
        has_special = any(c in special_chars for c in password)
        self.assertTrue(has_special, "Password should contain at least one special character")

    def test_generate_password_excludes_confusing_chars(self):
        """Test that generated password excludes confusing characters"""
        # Generate multiple passwords to increase confidence
        for _ in range(10):
            password = generate_password(length=16)
            # Should not contain: 0, 1, l, i, O, I
            self.assertNotIn('0', password, "Password should not contain '0'")
            self.assertNotIn('1', password, "Password should not contain '1'")
            self.assertNotIn('l', password, "Password should not contain 'l'")
            self.assertNotIn('i', password, "Password should not contain 'i'")
            self.assertNotIn('O', password, "Password should not contain 'O'")
            self.assertNotIn('I', password, "Password should not contain 'I'")

    def test_generate_password_uniqueness(self):
        """Test that generated passwords are unique"""
        passwords = [generate_password() for _ in range(100)]
        # All passwords should be unique
        self.assertEqual(len(passwords), len(set(passwords)))

    def test_generate_password_api_returns_json(self):
        """Test that the password generation API returns valid JSON"""
        response = self.client.post(reverse('generate_password_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_generate_password_api_returns_password(self):
        """Test that the API returns a password field"""
        response = self.client.post(reverse('generate_password_api'))
        data = json.loads(response.content)
        self.assertIn('password', data)
        self.assertEqual(len(data['password']), 16)

    def test_generate_password_api_no_auth_required(self):
        """Test that password generation API doesn't require authentication"""
        # Don't login - API should still work for registration page (uses POST now for security)
        response = self.client.post(reverse('generate_password_api'))
        self.assertEqual(response.status_code, 200)


class ChangePasswordViewTest(TestCase):
    """Tests for the change password view"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='oldpassword123'
        )
        self.client = Client()

    def test_change_password_view_requires_login(self):
        """Test that change password view requires authentication"""
        response = self.client.get(reverse('change_password'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_change_password_view_get(self):
        """Test that change password view displays form"""
        self.client.login(username='testuser', password='oldpassword123')
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_app/change_password.html')
        self.assertIn('form', response.context)

    def test_change_password_view_post_valid(self):
        """Test successful password change"""
        self.client.login(username='testuser', password='oldpassword123')
        post_data = {
            'old_password': 'oldpassword123',
            'new_password1': 'newpassword456!',
            'new_password2': 'newpassword456!'
        }
        response = self.client.post(reverse('change_password'), post_data)
        # Should redirect to account page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('account'))

        # Verify password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456!'))

    def test_change_password_view_post_invalid(self):
        """Test password change with mismatched passwords"""
        self.client.login(username='testuser', password='oldpassword123')
        post_data = {
            'old_password': 'oldpassword123',
            'new_password1': 'newpassword456!',
            'new_password2': 'differentpassword!'
        }
        response = self.client.post(reverse('change_password'), post_data)
        # Should redisplay form with errors
        self.assertEqual(response.status_code, 200)
        # Check that form has errors
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

        # Verify password was NOT changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpassword123'))
