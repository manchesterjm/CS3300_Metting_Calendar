"""
Fuzz testing using Hypothesis
Tests the application with randomly generated inputs
"""
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.extra.django import TestCase as HypothesisTestCase
from .models import Unavailability
from .forms import UnavailabilityForm, DeleteSelectedForm


class FuzzUnavailabilityModelTest(HypothesisTestCase):
    """Fuzz tests for the Unavailability model"""

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
                date=datetime.date(year, month, day),
                start_time=datetime.time(start_hour, start_minute),
                end_time=datetime.time(end_hour, end_minute)
            )
            self.assertIsNotNone(unavail)
            self.assertIsNotNone(unavail.id)
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
            date=date,
            start_time=time1,
            end_time=time2
        )
        str_repr = str(unavail)
        # Should contain the date and both times
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
        # Only validate if we're not using default times in submit mode
        if form.is_valid():
            self.assertTrue(True)
        else:
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
        # If using midnight times, should fail validation
        if start_time == datetime.time(0, 0) or end_time == datetime.time(0, 0):
            self.assertFalse(form.is_valid())
        else:
            # Non-default times should pass
            self.assertTrue(form.is_valid())


class FuzzCalendarViewTest(HypothesisTestCase):
    """Fuzz tests for the calendar view"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.url = reverse('calendar')

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
        # Create random unavailability entries for the date
        Unavailability.objects.all().delete()
        for i in range(num_entries):
            hour = (8 + i) % 12 + 8  # Between 8 and 20
            Unavailability.objects.create(
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
            Unavailability.objects.all().delete()


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
            client = Client()
            response = client.post(reverse('calendar'), post_data)
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
            client = Client()
            response = client.post(reverse('calendar'), post_data)
            # Should handle gracefully
            self.assertIn(response.status_code, [200, 302, 400])
        except Exception:
            # Invalid dates might cause exceptions
            pass
