"""
Debug tests for CRUD operations.

These tests print detailed information about what's happening during form submissions.
"""
import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Group, Unavailability


class DebugGroupCRUDTest(TestCase):
    """Debug tests for group calendar CRUD operations"""

    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.group = Group.objects.create(name='Test Group', created_by=self.user1)
        self.group.members.add(self.user1)

    def test_show_free_times_detailed(self):
        """Test show_free_times with detailed debugging using personal calendar"""
        self.client.login(username='user1', password='pass123')

        # Create a PERSONAL unavailability entry (not GroupUnavailability)
        entry = Unavailability.objects.create(
            user=self.user1,
            date=datetime.date(2025, 11, 2),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(14, 0),
            description='Grocery shopping'
        )
        print(f"\n[OK] Created personal unavailability entry: {entry}")

        # First, GET the page to see the read-only group calendar
        get_response = self.client.get(reverse('group_calendar', args=[self.group.id]))
        print(f"\n[OK] GET request status: {get_response.status_code}")

        # Now POST the show_free_times request
        post_data = {
            'date': '2025-11-02',
            'show_free_times': 'Show'
        }
        print(f"\n[OK] POST data: {post_data}")

        response = self.client.post(
            reverse('group_calendar', args=[self.group.id]),
            post_data
        )

        print(f"\n[OK] POST response status: {response.status_code}")
        print(f"[OK] Response context keys: {list(response.context.keys()) if hasattr(response, 'context') and response.context else 'No context'}")

        if hasattr(response, 'context') and response.context:
            free_times = response.context.get('free_times')
            print(f"[OK] free_times in context: {free_times is not None}")
            print(f"[OK] free_times value: {free_times}")
            print(f"[OK] free_times type: {type(free_times)}")
            if free_times:
                print(f"[OK] Number of free time slots: {len(free_times)}")
                print(f"[OK] First few slots: {free_times[:5] if len(free_times) > 5 else free_times}")

        # Assertions
        self.assertEqual(response.status_code, 200, "Should return 200 OK")
        self.assertIn('free_times', response.context, "free_times should be in context")
        self.assertIsNotNone(response.context['free_times'], "free_times should not be None")

        free_times = response.context['free_times']
        # 10:00-14:00 should be taken (8 half-hour slots) based on personal calendar
        self.assertNotIn('10:00', free_times)
        self.assertNotIn('13:30', free_times)
        # 8:00 and 14:00 should be free
        self.assertIn('08:00', free_times)
        self.assertIn('14:00', free_times)

        print("\n[OK] All assertions passed!")

    # OBSOLETE: Group calendar is now read-only and no longer supports show_last_five functionality
    # def test_show_last_five_detailed(self):
    #     """Test show_last_five with detailed debugging"""
    #     pass
