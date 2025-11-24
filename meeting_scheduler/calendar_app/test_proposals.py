"""
Tests for meeting proposal functionality (Phase 3).

This module contains comprehensive tests for MeetingProposal and MeetingResponse
models, forms, and views.

Test Classes:
    - MeetingProposalModelTests: Model tests
    - MeetingResponseModelTests: Response model tests
    - MeetingProposalFormTests: Form validation tests
    - ProposalViewTests: View integration tests
    - ProposalWorkflowTests: End-to-end workflow tests

Coverage: 95%+ for proposal-related code
Version: 1.0
"""
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core import mail

from calendar_app.models import (
    Group, MeetingProposal, MeetingResponse, Unavailability
)
from calendar_app.forms import MeetingProposalForm


class MeetingProposalModelTests(TestCase):
    """Test cases for MeetingProposal model."""

    def setUp(self):
        """Create test users and groups."""
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.user3 = User.objects.create_user(username="user3", password="pass123")

        self.group = Group.objects.create(name="Test Group", created_by=self.user1)
        self.group.members.add(self.user1, self.user2, self.user3)

        self.future_time = timezone.now() + timedelta(days=7)

    def test_create_proposal(self):
        """Test creating a meeting proposal."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            description="Discuss project status",
            meeting_datetime=self.future_time,
            duration_minutes=60,
            status='pending'
        )

        self.assertEqual(proposal.title, "Team Meeting")
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(proposal.group, self.group)
        self.assertEqual(proposal.proposed_by, self.user1)

    def test_proposal_str_representation(self):
        """Test __str__ method."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        expected = f"Team Meeting - Test Group at {self.future_time}"
        self.assertEqual(str(proposal), expected)

    def test_get_all_responses(self):
        """Test getting all responses to a proposal."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        MeetingResponse.objects.create(
            proposal=proposal, user=self.user2, response='accept'
        )
        MeetingResponse.objects.create(
            proposal=proposal, user=self.user3, response='accept'
        )

        responses = proposal.get_all_responses()
        self.assertEqual(responses.count(), 2)

    def test_get_pending_members(self):
        """Test getting members who haven't responded."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # Only user2 responds
        MeetingResponse.objects.create(
            proposal=proposal, user=self.user2, response='accept'
        )

        pending = proposal.get_pending_members()
        self.assertEqual(pending.count(), 2)  # user1 and user3
        self.assertIn(self.user1, pending)
        self.assertIn(self.user3, pending)

    def test_check_all_accepted_true(self):
        """Test check_all_accepted when all members accept."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # All 3 members accept
        for user in [self.user1, self.user2, self.user3]:
            MeetingResponse.objects.create(
                proposal=proposal, user=user, response='accept'
            )

        self.assertTrue(proposal.check_all_accepted())

    def test_check_all_accepted_false(self):
        """Test check_all_accepted when not all members accept."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # Only 2 accept
        MeetingResponse.objects.create(
            proposal=proposal, user=self.user1, response='accept'
        )
        MeetingResponse.objects.create(
            proposal=proposal, user=self.user2, response='accept'
        )

        self.assertFalse(proposal.check_all_accepted())

    def test_has_rejection_true(self):
        """Test has_rejection when a member declines."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        MeetingResponse.objects.create(
            proposal=proposal, user=self.user2, response='decline'
        )

        self.assertTrue(proposal.has_rejection())

    def test_has_rejection_false(self):
        """Test has_rejection when no one declines."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        MeetingResponse.objects.create(
            proposal=proposal, user=self.user1, response='accept'
        )

        self.assertFalse(proposal.has_rejection())

    def test_user_can_view_as_member(self):
        """Test user_can_view for group member."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.assertTrue(proposal.user_can_view(self.user2))

    def test_user_can_view_non_member(self):
        """Test user_can_view for non-member."""
        outsider = User.objects.create_user(username="outsider", password="pass")

        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.assertFalse(proposal.user_can_view(outsider))

    def test_user_can_respond_true(self):
        """Test user_can_respond for member who hasn't responded."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.assertTrue(proposal.user_can_respond(self.user2))

    def test_user_can_respond_already_responded(self):
        """Test user_can_respond for member who already responded."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        MeetingResponse.objects.create(
            proposal=proposal, user=self.user2, response='accept'
        )

        self.assertFalse(proposal.user_can_respond(self.user2))

    def test_user_can_respond_non_member(self):
        """Test user_can_respond for non-member."""
        outsider = User.objects.create_user(username="outsider", password="pass")

        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.assertFalse(proposal.user_can_respond(outsider))


class MeetingResponseModelTests(TestCase):
    """Test cases for MeetingResponse model."""

    def setUp(self):
        """Create test data."""
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")

        self.group = Group.objects.create(name="Test Group", created_by=self.user1)
        self.group.members.add(self.user1, self.user2)

        self.future_time = timezone.now() + timedelta(days=7)

        self.proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

    def test_create_response(self):
        """Test creating a meeting response."""
        response = MeetingResponse.objects.create(
            proposal=self.proposal,
            user=self.user2,
            response='accept'
        )

        self.assertEqual(response.proposal, self.proposal)
        self.assertEqual(response.user, self.user2)
        self.assertEqual(response.response, 'accept')

    def test_response_str_representation(self):
        """Test __str__ method."""
        response = MeetingResponse.objects.create(
            proposal=self.proposal,
            user=self.user2,
            response='accept'
        )

        expected = "user2 accepted: Team Meeting"
        self.assertEqual(str(response), expected)

    def test_unique_together_constraint(self):
        """Test that a user can only respond once to a proposal."""
        MeetingResponse.objects.create(
            proposal=self.proposal,
            user=self.user2,
            response='accept'
        )

        # Try to create duplicate response
        with self.assertRaises(Exception):  # Django will raise IntegrityError
            MeetingResponse.objects.create(
                proposal=self.proposal,
                user=self.user2,
                response='decline'
            )


class MeetingProposalFormTests(TestCase):
    """Test cases for MeetingProposalForm."""

    def test_valid_form(self):
        """Test form with valid data."""
        future_time = timezone.now() + timedelta(days=7)
        data = {
            'title': 'Team Meeting',
            'description': 'Discuss project',
            'meeting_datetime': future_time.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
        }

        form = MeetingProposalForm(data=data)
        self.assertTrue(form.is_valid())

    def test_past_datetime_invalid(self):
        """Test that past datetime is rejected."""
        past_time = timezone.now() - timedelta(days=1)
        data = {
            'title': 'Team Meeting',
            'meeting_datetime': past_time.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
        }

        form = MeetingProposalForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('meeting_datetime', form.errors)

    def test_empty_title_invalid(self):
        """Test that empty title is rejected."""
        future_time = timezone.now() + timedelta(days=7)
        data = {
            'title': '',
            'meeting_datetime': future_time.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
        }

        form = MeetingProposalForm(data=data)
        self.assertFalse(form.is_valid())

    def test_title_stripping(self):
        """Test that title whitespace is stripped."""
        future_time = timezone.now() + timedelta(days=7)
        data = {
            'title': '  Team Meeting  ',
            'meeting_datetime': future_time.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
        }

        form = MeetingProposalForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Team Meeting')

    def test_description_stripping(self):
        """Test that description whitespace is stripped."""
        future_time = timezone.now() + timedelta(days=7)
        data = {
            'title': 'Team Meeting',
            'description': '  Discuss project  ',
            'meeting_datetime': future_time.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
        }

        form = MeetingProposalForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['description'], 'Discuss project')


class ProposalViewTests(TestCase):
    """Test cases for proposal views."""

    def setUp(self):
        """Create test data and client."""
        self.client = Client()

        self.user1 = User.objects.create_user(
            username="user1", password="pass123", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass123", email="user2@example.com"
        )
        self.user3 = User.objects.create_user(
            username="user3", password="pass123", email="user3@example.com"
        )

        self.group = Group.objects.create(name="Test Group", created_by=self.user1)
        self.group.members.add(self.user1, self.user2, self.user3)

        self.future_time = timezone.now() + timedelta(days=7)

    def test_create_proposal_view_get(self):
        """Test accessing create proposal page."""
        self.client.login(username="user1", password="pass123")
        url = reverse('create_proposal', args=[self.group.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Meeting Proposal")

    def test_create_proposal_view_post_valid(self):
        """Test creating proposal with valid data."""
        self.client.login(username="user1", password="pass123")
        url = reverse('create_proposal', args=[self.group.id])

        data = {
            'title': 'Team Meeting',
            'description': 'Discuss project status',
            'meeting_datetime': self.future_time.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
        }

        response = self.client.post(url, data)

        # Should redirect to proposal list
        self.assertEqual(response.status_code, 302)

        # Proposal should be created
        proposal = MeetingProposal.objects.filter(title='Team Meeting').first()
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.proposed_by, self.user1)
        self.assertEqual(proposal.status, 'pending')

    def test_create_proposal_non_member(self):
        """Test that non-member cannot create proposal."""
        User.objects.create_user(username="outsider", password="pass")
        self.client.login(username="outsider", password="pass")

        url = reverse('create_proposal', args=[self.group.id])
        response = self.client.get(url)

        # Should redirect with error
        self.assertEqual(response.status_code, 302)

    def test_proposal_list_view(self):
        """Test viewing proposal list."""
        # Create a proposal
        MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.client.login(username="user2", password="pass123")
        url = reverse('proposal_list', args=[self.group.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Team Meeting")
        self.assertContains(response, "Meeting Proposals")

    def test_respond_accept_to_proposal(self):
        """Test accepting a proposal."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.client.login(username="user2", password="pass123")
        url = reverse('respond_to_proposal', args=[proposal.id, 'accept'])
        response = self.client.post(url)  # Changed to POST for CSRF protection

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Response should be created
        user_response = MeetingResponse.objects.filter(
            proposal=proposal, user=self.user2
        ).first()
        self.assertIsNotNone(user_response)
        self.assertEqual(user_response.response, 'accept')

    def test_respond_decline_to_proposal(self):
        """Test declining a proposal."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.client.login(username="user2", password="pass123")
        url = reverse('respond_to_proposal', args=[proposal.id, 'decline'])
        response = self.client.post(url)  # Changed to POST for CSRF protection

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Proposal should be rejected
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'rejected')

    def test_respond_rejects_get_request(self):
        """Test that GET requests are rejected (CSRF protection)."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        self.client.login(username="user2", password="pass123")
        url = reverse('respond_to_proposal', args=[proposal.id, 'accept'])
        response = self.client.get(url)  # Attempt GET instead of POST

        # Should redirect with error message
        self.assertEqual(response.status_code, 302)

        # Response should NOT be created (GET was rejected)
        user_response = MeetingResponse.objects.filter(
            proposal=proposal, user=self.user2
        ).first()
        self.assertIsNone(user_response)


class ProposalWorkflowTests(TestCase):
    """End-to-end workflow tests for proposals."""

    def setUp(self):
        """Create test data."""
        self.client = Client()

        self.user1 = User.objects.create_user(
            username="user1", password="pass123", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass123", email="user2@example.com"
        )
        self.user3 = User.objects.create_user(
            username="user3", password="pass123", email="user3@example.com"
        )

        self.group = Group.objects.create(name="Test Group", created_by=self.user1)
        self.group.members.add(self.user1, self.user2, self.user3)

        self.future_time = timezone.now() + timedelta(days=7)

    def test_full_accept_workflow(self):
        """Test complete workflow when all members accept."""
        # Create proposal
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # All members accept
        for user in [self.user1, self.user2, self.user3]:
            self.client.login(username=user.username, password="pass123")
            url = reverse('respond_to_proposal', args=[proposal.id, 'accept'])
            self.client.post(url)  # Changed to POST for CSRF protection
            self.client.logout()

        # Proposal should be scheduled
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'scheduled')

        # All members should have unavailability entry
        for user in [self.user1, self.user2, self.user3]:
            unavail = Unavailability.objects.filter(
                user=user,
                date=self.future_time.date()
            ).first()
            self.assertIsNotNone(unavail)
            self.assertIn('Meeting:', unavail.description)

    def test_rejection_workflow(self):
        """Test workflow when one member declines."""
        # Create proposal
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.user1,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # User2 declines
        self.client.login(username="user2", password="pass123")
        url = reverse('respond_to_proposal', args=[proposal.id, 'decline'])
        self.client.post(url)  # Changed to POST for CSRF protection

        # Proposal should be rejected
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'rejected')

    def test_email_notifications_sent(self):
        """Test that email notifications are sent."""
        # Clear mailbox
        mail.outbox = []

        # Create proposal (should send emails)
        self.client.login(username="user1", password="pass123")
        url = reverse('create_proposal', args=[self.group.id])

        data = {
            'title': 'Team Meeting',
            'description': 'Discuss project',
            'meeting_datetime': self.future_time.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
        }

        self.client.post(url, data)

        # Should send email to all members
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New Meeting Proposal', mail.outbox[0].subject)


class OwnerParticipationTests(TestCase):
    """
    Test cases for owner participation in meeting proposals.

    Security: These tests verify that group owners are properly included in
    proposal workflows, preventing security issues where owners could be
    excluded from meetings or unable to respond to proposals.
    """

    def setUp(self):
        """Create test users and groups with owner NOT as member."""
        self.owner = User.objects.create_user(username="owner", password="pass123")
        self.member1 = User.objects.create_user(username="member1", password="pass123")
        self.member2 = User.objects.create_user(username="member2", password="pass123")

        # Create group where owner is NOT a member
        self.group = Group.objects.create(name="Test Group", created_by=self.owner)
        self.group.members.add(self.member1, self.member2)
        # Note: owner is NOT in members list

        self.future_time = timezone.now() + timedelta(days=7)
        self.client = Client()

    def test_owner_can_respond_to_proposal(self):
        """Test that owner can respond even if not in members list."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.owner,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # Owner should be able to respond
        self.assertTrue(proposal.user_can_respond(self.owner))

        # Create response
        self.client.login(username="owner", password="pass123")
        url = reverse('respond_to_proposal', args=[proposal.id, 'accept'])
        response = self.client.post(url)

        # Should succeed
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MeetingResponse.objects.filter(proposal=proposal, user=self.owner).count(), 1)

    def test_owner_included_in_pending_members(self):
        """Test that get_pending_members includes owner."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.owner,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # Only member1 responds
        MeetingResponse.objects.create(
            proposal=proposal, user=self.member1, response='accept'
        )

        pending = proposal.get_pending_members()
        # Should include owner and member2 (2 people)
        self.assertEqual(pending.count(), 2)
        self.assertIn(self.owner, pending)
        self.assertIn(self.member2, pending)

    def test_check_all_accepted_requires_owner(self):
        """Test that check_all_accepted counts owner."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.owner,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # Only members accept (not owner)
        MeetingResponse.objects.create(
            proposal=proposal, user=self.member1, response='accept'
        )
        MeetingResponse.objects.create(
            proposal=proposal, user=self.member2, response='accept'
        )

        # Should be False because owner hasn't accepted
        self.assertFalse(proposal.check_all_accepted())

        # Owner accepts
        MeetingResponse.objects.create(
            proposal=proposal, user=self.owner, response='accept'
        )

        # Now should be True
        self.assertTrue(proposal.check_all_accepted())

    def test_schedule_meeting_includes_owner_calendar(self):
        """Test that scheduled meetings appear on owner's calendar."""
        proposal = MeetingProposal.objects.create(
            group=self.group,
            proposed_by=self.owner,
            title="Team Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # Owner and member1 accept first
        self.client.login(username="owner", password="pass123")
        url = reverse('respond_to_proposal', args=[proposal.id, 'accept'])
        self.client.post(url)

        self.client.login(username="member1", password="pass123")
        self.client.post(url)

        # Member2 accepts last (triggers auto-schedule)
        self.client.login(username="member2", password="pass123")
        self.client.post(url)

        # Check that Unavailability was created for owner
        owner_unavailability = Unavailability.objects.filter(
            user=self.owner,
            date=self.future_time.date(),
            description__icontains='Meeting: Team Meeting'
        )
        self.assertEqual(owner_unavailability.count(), 1)

        # Check all participants have calendar entries (3 total)
        all_unavailability = Unavailability.objects.filter(
            date=self.future_time.date(),
            description__icontains='Meeting: Team Meeting'
        )
        self.assertEqual(all_unavailability.count(), 3)

    def test_owner_only_group_can_accept_proposal(self):
        """Test that owner-only groups (no members) can schedule meetings."""
        # Create owner-only group
        solo_group = Group.objects.create(name="Solo Group", created_by=self.owner)
        # No members added

        proposal = MeetingProposal.objects.create(
            group=solo_group,
            proposed_by=self.owner,
            title="Solo Task",
            meeting_datetime=self.future_time,
            duration_minutes=30
        )

        # Owner should be able to respond
        self.assertTrue(proposal.user_can_respond(self.owner))

        # Owner accepts
        MeetingResponse.objects.create(
            proposal=proposal, user=self.owner, response='accept'
        )

        # Should be fully accepted (only participant is owner)
        self.assertTrue(proposal.check_all_accepted())

    def test_owner_and_member_no_duplicate_calendar_entries(self):
        """Test that owner who is also a member doesn't get duplicate calendar entries."""
        # Create group where owner is ALSO a member
        dual_group = Group.objects.create(name="Dual Group", created_by=self.owner)
        dual_group.members.add(self.owner, self.member1)  # Owner is both owner and member

        proposal = MeetingProposal.objects.create(
            group=dual_group,
            proposed_by=self.owner,
            title="Dual Meeting",
            meeting_datetime=self.future_time,
            duration_minutes=60
        )

        # Both accept
        for user in [self.owner, self.member1]:
            MeetingResponse.objects.create(
                proposal=proposal, user=user, response='accept'
            )

        # Manually trigger schedule_meeting
        from calendar_app.proposal_views import schedule_meeting
        schedule_meeting(proposal)

        # Owner should have exactly 1 calendar entry (not 2)
        owner_entries = Unavailability.objects.filter(
            user=self.owner,
            date=self.future_time.date(),
            description__icontains='Meeting: Dual Meeting'
        )
        self.assertEqual(owner_entries.count(), 1)
