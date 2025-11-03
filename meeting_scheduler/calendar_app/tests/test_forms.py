"""
Form tests for calendar_app

Tests for:
- UnavailabilityForm
- DeleteSelectedForm
- GroupCreateForm
- AddMemberForm
- GroupUnavailabilityForm

Covers form validation, field validation, and error handling.
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from calendar_app.models import Group
from calendar_app.forms import (
    UnavailabilityForm,
    DeleteSelectedForm,
    GroupCreateForm,
    AddMemberForm,
    GroupUnavailabilityForm
)


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
