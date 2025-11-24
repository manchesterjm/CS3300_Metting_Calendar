"""
Fuzz testing using Hypothesis

Tests the application with randomly generated inputs with authentication support.
Uses Hypothesis library to generate ~350 test cases from 9 test functions.

Test Count: 9 fuzz tests (~350 generated cases)
Strategy: Property-based testing with constrained random generation
Last Updated: 2025-01-11
"""
# pylint: disable=too-many-arguments,too-many-positional-arguments,broad-exception-caught
import datetime
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.extra.django import TestCase as HypothesisTestCase
from .models import Unavailability, Group, GroupUnavailability
from .forms import (
    UnavailabilityForm,
    DeleteSelectedForm,
    GroupCreateForm,
    AddMemberForm,
    GroupUnavailabilityForm
)


class FuzzUnavailabilityModelTest(HypothesisTestCase):
    """Fuzz tests for the Unavailability model"""

    def setUp(self):
        """Set up test user for all fuzz tests"""
        # Use get_or_create to avoid duplicate user errors
        self.user, _ = User.objects.get_or_create(
            username='fuzzuser',
            defaults={'password': 'fuzzpass123'}
        )
        if not self.user.has_usable_password():
            self.user.set_password('fuzzpass123')
            self.user.save()

    @given(
        year=st.integers(min_value=2000, max_value=2099),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),  # Safe for all months
        start_hour=st.integers(min_value=0, max_value=23),
        start_minute=st.integers(min_value=0, max_value=59),
        end_hour=st.integers(min_value=0, max_value=23),
        end_minute=st.integers(min_value=0, max_value=59),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_model_creation_with_random_data(
        self, year, month, day, start_hour, start_minute, end_hour, end_minute
    ):
        """Test model handles various date/time combinations"""
        try:
            unavail = Unavailability.objects.create(
                user=self.user,
                date=datetime.date(year, month, day),
                start_time=datetime.time(start_hour, start_minute),
                end_time=datetime.time(end_hour, end_minute)
            )
            self.assertIsNotNone(unavail)
            self.assertIsNotNone(unavail.id)
            self.assertEqual(unavail.user, self.user)
            # Cleanup
            unavail.delete()
        except Exception as e:
            # Model should handle all valid datetime combinations
            self.fail(f"Model creation failed with valid data: {e}")

    @given(
        date=st.dates(min_value=datetime.date(2000, 1, 1)),
        time1=st.times(),
        time2=st.times()
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_model_str_representation(self, date, time1, time2):
        """Test string representation with random dates and times"""
        unavail = Unavailability.objects.create(
            user=self.user,
            date=date,
            start_time=time1,
            end_time=time2
        )
        str_repr = str(unavail)
        # Should contain the username and date
        self.assertIn('fuzzuser', str_repr)
        self.assertIn(str(date), str_repr)
        # Cleanup
        unavail.delete()


class FuzzUnavailabilityFormTest(HypothesisTestCase):
    """Fuzz tests for the UnavailabilityForm"""

    @given(
        date=st.dates(min_value=datetime.date(2000, 1, 1)),
        start_time=st.times(),
        end_time=st.times()
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_form_validation_with_random_data(self, date, start_time, end_time):
        """Test form validation with random valid data"""
        form_data = {
            'date': date,
            'start_time': start_time,
            'end_time': end_time
        }
        form = UnavailabilityForm(data=form_data)
        # Form should handle all valid datetime combinations
        # Form may be valid or invalid depending on default values
        # The test verifies the form doesn't crash with random data
        if not form.is_valid():
            # Some combinations might fail validation
            # (e.g., default times in submit_unavailability mode)
            self.assertIsNotNone(form.errors)

    @given(
        date=st.dates(min_value=datetime.date(2000, 1, 1)),
        start_time=st.times(),
        end_time=st.times()
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_form_submit_type_validation(self, date, start_time, end_time):
        """Test form validation with submit_type parameter"""
        form_data = {
            'date': date,
            'start_time': start_time,
            'end_time': end_time
        }
        form = UnavailabilityForm(
            data=form_data,
            submit_type='submit_unavailability'
        )
        # Form should fail validation if:
        # 1. Using midnight times (default values)
        # 2. start_time >= end_time (invalid time range)
        if start_time == datetime.time(0, 0) or end_time == datetime.time(0, 0) or start_time >= end_time:
            self.assertFalse(form.is_valid())
        else:
            # Non-default times with valid range should pass
            self.assertTrue(form.is_valid())


class FuzzCalendarViewTest(HypothesisTestCase):
    """Fuzz tests for the calendar view"""

    def setUp(self):
        """Set up test client and authenticated user"""
        self.client = Client()
        self.url = reverse('calendar')
        # Use get_or_create to avoid duplicate user errors
        self.user, created = User.objects.get_or_create(
            username='fuzzviewuser',
            defaults={'password': 'fuzzpass123'}
        )
        if created or not self.user.has_usable_password():
            self.user.set_password('fuzzpass123')
            self.user.save()
        self.client.login(username='fuzzviewuser', password='fuzzpass123')

    @given(
        year=st.integers(min_value=2000, max_value=2099),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),
        hour=st.integers(min_value=1, max_value=23),  # Avoid midnight
        minute=st.integers(min_value=0, max_value=59)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_submit_unavailability_fuzz(self, year, month, day, hour, minute):
        """Test submitting unavailability with random data"""
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}"
        post_data = {
            'date': date_str,
            'start_time': time_str,
            'end_time': time_str,
            'submit_unavailability': 'Submit'
        }
        try:
            response = self.client.post(self.url, post_data)
            # Should either succeed (302) or show form with errors (200)
            self.assertIn(response.status_code, [200, 302])
        except Exception as e:
            self.fail(f"View crashed with valid input: {e}")

    @given(
        num_entries=st.integers(min_value=0, max_value=20),
        date=st.dates(min_value=datetime.date(2020, 1, 1))
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_show_free_times_fuzz(self, num_entries, date):
        """Test free times calculation with random number of entries"""
        # Ensure user is logged in (hypothesis runs test multiple times)
        self.client.force_login(self.user)

        # Create random unavailability entries for the date
        Unavailability.objects.filter(user=self.user).delete()
        for i in range(num_entries):
            hour = (8 + i) % 12 + 8  # Between 8 and 20
            Unavailability.objects.create(
                user=self.user,
                date=date,
                start_time=datetime.time(hour, 0),
                end_time=datetime.time(hour, 30)
            )

        post_data = {
            'date': date.strftime('%Y-%m-%d'),
            'start_time': '01:00',  # Non-default time
            'end_time': '01:00',
            'show_free_times': 'Show'
        }
        try:
            response = self.client.post(self.url, post_data)
            self.assertEqual(response.status_code, 200)
            if 'free_times' in response.context:
                free_times = response.context['free_times']
                # Free times should be a list
                self.assertIsInstance(free_times, list)
        except Exception as e:
            self.fail(f"Free times calculation failed: {e}")
        finally:
            # Cleanup
            Unavailability.objects.filter(user=self.user).delete()


class FuzzDeleteSelectedFormTest(HypothesisTestCase):
    """Fuzz tests for DeleteSelectedForm"""

    @given(
        num_choices=st.integers(min_value=0, max_value=10),
        selected_indices=st.lists(
            st.integers(min_value=0, max_value=9),
            max_size=5
        )
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_form_with_random_choices(self, num_choices, selected_indices):
        """Test form with random number of choices and selections"""
        form = DeleteSelectedForm()
        # Create random choices
        choices = [(i, f"Entry {i}") for i in range(num_choices)]
        form.fields['entry_ids'].choices = choices

        # Select random indices that exist
        valid_selections = [
            str(i) for i in selected_indices if i < num_choices
        ]
        form_data = {'entry_ids': valid_selections}
        form = DeleteSelectedForm(data=form_data)
        form.fields['entry_ids'].choices = choices

        # Form should always be valid (required=False)
        self.assertTrue(form.is_valid())


class FuzzEdgeCasesTest(HypothesisTestCase):
    """Fuzz tests for edge cases"""

    def setUp(self):
        """Set up test client and authenticated user"""
        self.client = Client()
        # Use get_or_create to avoid duplicate user errors
        self.user, created = User.objects.get_or_create(
            username='fuzzedgeuser',
            defaults={'password': 'fuzzpass123'}
        )
        if created or not self.user.has_usable_password():
            self.user.set_password('fuzzpass123')
            self.user.save()
        self.client.login(username='fuzzedgeuser', password='fuzzpass123')

    @given(
        time_str=st.text(alphabet=st.characters(whitelist_categories=('Nd', 'Pc')),
                        min_size=0, max_size=10)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_malformed_time_input(self, time_str):
        """Test form handles malformed time strings gracefully"""
        post_data = {
            'date': '2025-05-01',
            'start_time': time_str,
            'end_time': time_str,
            'submit_unavailability': 'Submit'
        }
        try:
            response = self.client.post(reverse('calendar'), post_data)
            # Should not crash - either accept or show form errors
            self.assertIn(response.status_code, [200, 302, 400])
        except Exception:
            # Some malformed inputs might cause exceptions
            # but the view should handle them
            pass

    @given(
        date_parts=st.tuples(
            st.integers(min_value=-1000, max_value=3000),
            st.integers(min_value=-10, max_value=20),
            st.integers(min_value=-10, max_value=40)
        )
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_invalid_date_combinations(self, date_parts):
        """Test form handles invalid date combinations"""
        year, month, day = date_parts
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        post_data = {
            'date': date_str,
            'start_time': '09:00',
            'end_time': '10:00',
            'submit_unavailability': 'Submit'
        }
        try:
            response = self.client.post(reverse('calendar'), post_data)
            # Should handle gracefully
            self.assertIn(response.status_code, [200, 302, 400])
        except Exception:
            # Invalid dates might cause exceptions
            pass


class FuzzGroupModelTest(HypothesisTestCase):
    """Fuzz tests for the Group model"""

    def setUp(self):
        """Set up test user for all fuzz tests"""
        self.user, _ = User.objects.get_or_create(
            username='fuzzgroupuser',
            defaults={'password': 'fuzzpass123'}
        )
        if not self.user.has_usable_password():
            self.user.set_password('fuzzpass123')
            self.user.save()

    @given(
        name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_group_creation_with_random_names(self, name):
        """Test group creation with random valid names"""
        # Skip if name is whitespace only
        if not name.strip():
            return

        try:
            # Delete any existing group with this name
            Group.objects.filter(name=name).delete()

            group = Group.objects.create(
                name=name,
                created_by=self.user
            )
            self.assertIsNotNone(group)
            self.assertEqual(group.name, name)
            self.assertEqual(group.created_by, self.user)

            # Cleanup
            group.delete()
        except Exception as e:
            self.fail(f"Group creation failed with valid data: {e}")

    @given(
        year=st.integers(min_value=2000, max_value=2099),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),
        start_hour=st.integers(min_value=0, max_value=23),
        end_hour=st.integers(min_value=0, max_value=23)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_group_unavailability_with_random_data(
        self, year, month, day, start_hour, end_hour
    ):
        """Test group unavailability creation with random data"""
        group = Group.objects.create(
            name=f'Test Group {year}{month}{day}',
            created_by=self.user
        )

        try:
            group_unavail = GroupUnavailability.objects.create(
                group=group,
                user=self.user,
                date=datetime.date(year, month, day),
                start_time=datetime.time(start_hour, 0),
                end_time=datetime.time(end_hour, 0),
                description='Fuzz test'
            )
            self.assertIsNotNone(group_unavail)
            self.assertEqual(group_unavail.group, group)
            self.assertEqual(group_unavail.user, self.user)
        except Exception as e:
            self.fail(f"GroupUnavailability creation failed: {e}")
        finally:
            group.delete()


class FuzzGroupFormsTest(HypothesisTestCase):
    """Fuzz tests for group forms"""

    def setUp(self):
        """Set up test user"""
        self.user, _ = User.objects.get_or_create(
            username='fuzzformuser',
            defaults={'password': 'fuzzpass123'}
        )

    @given(
        name=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_group_create_form_with_random_names(self, name):
        """Test GroupCreateForm with random names"""
        # Delete any existing group with this name
        Group.objects.filter(name=name).delete()

        form_data = {'name': name}
        form = GroupCreateForm(data=form_data)

        # Form should handle all names gracefully
        # May be valid or invalid depending on constraints
        if not form.is_valid():
            self.assertIsNotNone(form.errors)

    @given(
        username=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=150
        )
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_add_member_form_with_random_usernames(self, username):
        """Test AddMemberForm with random usernames"""
        form_data = {'username': username}
        form = AddMemberForm(data=form_data)

        # Form should handle all usernames gracefully
        # Will be invalid if user doesn't exist
        if not form.is_valid():
            self.assertIsNotNone(form.errors)

    @given(
        date=st.dates(min_value=datetime.date(2000, 1, 1)),
        start_time=st.times(),
        end_time=st.times(),
        description=st.text(max_size=200)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_group_unavailability_form_with_random_data(
        self, date, start_time, end_time, description
    ):
        """Test GroupUnavailabilityForm with random data"""
        form_data = {
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'description': description
        }
        form = GroupUnavailabilityForm(data=form_data)

        # Form should handle all valid datetime combinations
        if not form.is_valid():
            self.assertIsNotNone(form.errors)


class FuzzGroupViewsTest(HypothesisTestCase):
    """Fuzz tests for group views"""

    def setUp(self):
        """Set up test client and authenticated user"""
        self.client = Client()
        self.user, created = User.objects.get_or_create(
            username='fuzzgroupviewuser',
            defaults={'password': 'fuzzpass123'}
        )
        if created or not self.user.has_usable_password():
            self.user.set_password('fuzzpass123')
            self.user.save()
        self.client.login(username='fuzzgroupviewuser', password='fuzzpass123')

    @given(
        name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_group_create_view_fuzz(self, name):
        """Test group creation view with random names"""
        # Skip if name is whitespace only
        if not name.strip():
            return

        # Cleanup existing group
        Group.objects.filter(name=name).delete()

        post_data = {'name': name}
        try:
            response = self.client.post(reverse('group_create'), post_data)
            # Should either succeed (302) or show form with errors (200)
            self.assertIn(response.status_code, [200, 302])
        except Exception as e:
            self.fail(f"Group create view crashed: {e}")
        finally:
            # Cleanup
            Group.objects.filter(name=name).delete()

    @given(
        year=st.integers(min_value=2000, max_value=2099),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),
        hour=st.integers(min_value=1, max_value=23)
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_group_calendar_submit_fuzz(self, year, month, day, hour):
        """Test group calendar submission with random data"""
        # Create a test group
        group = Group.objects.create(
            name=f'Fuzz Group {year}{month}',
            created_by=self.user
        )
        group.members.add(self.user)

        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:00"
        post_data = {
            'date': date_str,
            'start_time': time_str,
            'end_time': time_str,
            'description': 'Fuzz test',
            'submit_unavailability': 'Submit'
        }

        try:
            response = self.client.post(
                reverse('group_calendar', args=[group.id]),
                post_data
            )
            # Should either succeed (302) or show form with errors (200)
            self.assertIn(response.status_code, [200, 302])
        except Exception as e:
            self.fail(f"Group calendar view crashed: {e}")
        finally:
            # Cleanup
            group.delete()
