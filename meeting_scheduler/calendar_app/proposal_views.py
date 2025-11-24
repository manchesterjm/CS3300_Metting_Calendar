"""
Views for meeting proposal functionality.

This module handles all meeting proposal-related views including:
- Creating new meeting proposals
- Listing proposals for a group
- Responding to proposals (accept/decline)
- Auto-scheduling when all members accept

All views require authentication and appropriate group membership.
"""
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import Group, MeetingProposal, MeetingResponse, Unavailability
from .forms import MeetingProposalForm


@login_required
def create_proposal_view(request, group_id):
    """
    Create a new meeting proposal for a group.

    Only group members can create proposals. Upon creation, all group members
    are notified via email.

    Args:
        request: HttpRequest object
        group_id: ID of the group for which to create the proposal

    Returns:
        HttpResponse: Rendered template or redirect
    """
    group = get_object_or_404(Group, id=group_id)

    # Check if user is a member of the group
    if not group.is_member(request.user) and not group.is_owner(request.user):
        messages.error(request, 'You must be a member of this group to create proposals.')
        return redirect('group_list')

    if request.method == 'POST':
        form = MeetingProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.group = group
            proposal.proposed_by = request.user
            proposal.status = 'pending'
            proposal.save()

            # Send email notifications to all group members
            send_proposal_notifications(proposal)

            messages.success(
                request,
                f'Meeting proposal "{proposal.title}" created successfully. '
                f'All group members have been notified.'
            )
            return redirect('proposal_list', group_id=group.id)
    else:
        form = MeetingProposalForm()

    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'calendar_app/create_proposal.html', context)


@login_required
def proposal_list_view(request, group_id):
    """
    List all meeting proposals for a group.

    Shows pending, accepted, rejected, and scheduled proposals.
    Only group members can view proposals.

    Args:
        request: HttpRequest object
        group_id: ID of the group

    Returns:
        HttpResponse: Rendered template with proposal list
    """
    group = get_object_or_404(Group, id=group_id)

    # Check if user is a member of the group
    if not group.user_can_view(request.user):
        messages.error(request, 'You do not have permission to view this group.')
        return redirect('group_list')

    # Get all proposals for this group
    proposals = MeetingProposal.objects.filter(group=group).order_by('-created_at')

    # Annotate each proposal with user's response status
    for proposal in proposals:
        user_response = MeetingResponse.objects.filter(
            proposal=proposal,
            user=request.user
        ).first()
        proposal.user_response = user_response
        proposal.pending_count = proposal.get_pending_members().count()
        proposal.accepted_count = proposal.responses.filter(response='accept').count()
        proposal.declined_count = proposal.responses.filter(response='decline').count()

    context = {
        'group': group,
        'proposals': proposals,
    }
    return render(request, 'calendar_app/proposal_list.html', context)


@login_required
def respond_to_proposal_view(request, proposal_id, response_type):
    """
    Handle user response to a meeting proposal.

    Allows group members to accept or decline a proposal.
    When all members accept, the meeting is auto-scheduled.

    Args:
        request: HttpRequest object
        proposal_id: ID of the proposal
        response_type: 'accept' or 'decline'

    Returns:
        HttpResponse: Redirect to proposal list
    """
    proposal = get_object_or_404(MeetingProposal, id=proposal_id)

    # Check if user can respond
    if not proposal.user_can_respond(request.user):
        messages.error(
            request,
            'You cannot respond to this proposal. You may have already responded '
            'or are not a member of this group.'
        )
        return redirect('proposal_list', group_id=proposal.group.id)

    # Validate response type
    if response_type not in ['accept', 'decline']:
        messages.error(request, 'Invalid response type.')
        return redirect('proposal_list', group_id=proposal.group.id)

    # Create the response
    MeetingResponse.objects.create(
        proposal=proposal,
        user=request.user,
        response=response_type
    )

    # Check if meeting should be auto-scheduled or rejected
    if response_type == 'decline':
        proposal.status = 'rejected'
        proposal.save()
        messages.info(
            request,
            f'You declined "{proposal.title}". The proposal has been rejected.'
        )
        # Notify proposer of rejection
        notify_proposal_rejected(proposal, request.user)

    elif proposal.check_all_accepted():
        # All members accepted - auto-schedule the meeting
        proposal.status = 'accepted'
        proposal.save()
        schedule_meeting(proposal)
        messages.success(
            request,
            f'All members accepted "{proposal.title}"! The meeting has been scheduled '
            f'and added to everyone\'s calendars.'
        )
        # Notify all members of successful scheduling
        notify_meeting_scheduled(proposal)

    else:
        # Still waiting for responses
        pending_count = proposal.get_pending_members().count()
        messages.success(
            request,
            f'You accepted "{proposal.title}". Waiting for {pending_count} more member(s).'
        )

    return redirect('proposal_list', group_id=proposal.group.id)


def send_proposal_notifications(proposal):
    """
    Send email notifications to all group members about a new proposal.

    Args:
        proposal: MeetingProposal instance
    """
    members = proposal.group.members.all()
    subject = f'New Meeting Proposal: {proposal.title}'
    message = f"""
A new meeting has been proposed for your group "{proposal.group.name}":

Title: {proposal.title}
Proposed by: {proposal.proposed_by.username}
Date & Time: {proposal.meeting_datetime.strftime('%Y-%m-%d at %I:%M %p')}
Duration: {proposal.get_duration_minutes_display()}

{proposal.description}

Please log in to respond to this proposal.
"""

    recipient_list = [member.email for member in members if member.email]
    if recipient_list:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=True,
        )


def notify_proposal_rejected(proposal, declining_user):
    """
    Notify the proposer that their proposal was rejected.

    Args:
        proposal: MeetingProposal instance
        declining_user: User who declined the proposal
    """
    subject = f'Meeting Proposal Rejected: {proposal.title}'
    message = f"""
Your meeting proposal "{proposal.title}" for group "{proposal.group.name}" has been rejected.

{declining_user.username} declined the proposal.
"""

    if proposal.proposed_by.email:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [proposal.proposed_by.email],
            fail_silently=True,
        )


def notify_meeting_scheduled(proposal):
    """
    Notify all group members that a meeting has been successfully scheduled.

    Args:
        proposal: MeetingProposal instance
    """
    members = proposal.group.members.all()
    subject = f'Meeting Scheduled: {proposal.title}'
    message = f"""
Great news! The meeting "{proposal.title}" has been scheduled.

All members accepted the proposal.

Date & Time: {proposal.meeting_datetime.strftime('%Y-%m-%d at %I:%M %p')}
Duration: {proposal.get_duration_minutes_display()}
Group: {proposal.group.name}

The meeting has been added to your personal calendar.
"""

    recipient_list = [member.email for member in members if member.email]
    if recipient_list:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=True,
        )


def schedule_meeting(proposal):
    """
    Auto-schedule a meeting by creating Unavailability entries for all members.

    When all group members accept a proposal, this function creates unavailability
    entries on each member's personal calendar to block the meeting time.

    Args:
        proposal: MeetingProposal instance
    """
    # Calculate end time based on duration
    start_datetime = proposal.meeting_datetime
    end_datetime = start_datetime + timedelta(minutes=proposal.duration_minutes)

    # Create unavailability entry for each group member
    for member in proposal.group.members.all():
        Unavailability.objects.create(
            user=member,
            date=start_datetime.date(),
            start_time=start_datetime.time(),
            end_time=end_datetime.time(),
            description=f'Meeting: {proposal.title}'
        )

    # Update proposal status to scheduled
    proposal.status = 'scheduled'
    proposal.save()
