"""
Model tests for calendar_app

Tests for:
- Unavailability model
- Group model
- GroupUnavailability model

Covers model creation, string representations, field validation, and permission methods.
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from calendar_app.models import Unavailability, Group, GroupUnavailability


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
