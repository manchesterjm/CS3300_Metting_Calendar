"""
Django views for group calendar functionality.

This module contains views for managing groups and group calendars,
including group creation, member management, and shared calendar functionality.

Views:
    - group_list_view: Display all groups for current user
    - group_create_view: Create new calendar group
    - group_detail_view: View group details and members
    - group_calendar_view: Manage group unavailability entries
    - group_add_member_view: Add members to group
    - group_remove_member_view: Remove members from group
    - group_delete_view: Delete entire group

Features: Role-based access control (owner vs member permissions).
Version: 2.0
Security: All views require authentication and verify group membership
"""
import datetime
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError
from .forms import (
    GroupCreateForm,
    AddMemberForm,
    GroupUnavailabilityForm,
    GroupDeleteSelectedForm
)
from .models import Group, GroupUnavailability

# Configure logger for group calendar module
logger = logging.getLogger(__name__)


@login_required
def group_list_view(request):
    """
    Display all groups the user is a member of or owns.

    Shows a list of all groups where the user is either the owner or a member,
    with options to create new groups, view group calendars, or manage groups.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered group list template with user's groups.
    """
    # Get groups where user is a member OR owner
    # Optimize with prefetch_related to avoid N+1 queries when accessing members
    user_groups = request.user.calendar_groups.all() | request.user.owned_groups.all()
    user_groups = user_groups.distinct().select_related('created_by').prefetch_related('members').order_by('name')

    return render(request, 'calendar_app/group_list.html', {
        'groups': user_groups,
    })


@login_required
def group_create_view(request):
    """
    Create a new group and automatically add creator as first member.

    Handles group creation form submission. When a group is created,
    the creator is automatically set as the owner and added as the first member.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered group create template or redirect to group list.

    Redirects:
        - After successful group creation to group list view
    """
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            try:
                # Create group but don't save yet
                group = form.save(commit=False)
                group.created_by = request.user
                group.save()

                # Add creator as first member
                group.members.add(request.user)

                logger.info('User %s created group %s: %s', request.user.username, group.id, group.name)
                messages.success(request, f'Group "{group.name}" created successfully!')
                return redirect('group_list')
            except IntegrityError as e:
                logger.error('Integrity error creating group: %s', e)
                messages.error(request, 'A group with this name already exists.')
            except DatabaseError as e:
                logger.error('Database error creating group: %s', e)
                messages.error(request, 'An error occurred while creating the group.')
                return HttpResponseServerError('Internal server error')
    else:
        form = GroupCreateForm()

    return render(request, 'calendar_app/group_create.html', {
        'form': form,
    })


@login_required
def group_detail_view(request, group_id):
    """
    Show group details including members, creation info, and management options.

    Displays group information with member list and management options.
    Only members can view. Owner has additional options (add/remove members, delete group).

    Args:
        request: HttpRequest object containing metadata about the request.
        group_id: Primary key of the group to display.

    Returns:
        HttpResponse: Rendered group detail template.

    Raises:
        Http404: If group doesn't exist or user is not a member.
    """
    group = get_object_or_404(Group, id=group_id)

    # Check if user is a member (explicit permission check)
    if not (group.is_member(request.user) or group.is_owner(request.user)):
        logger.warning('Permission denied: User %s attempted to view group %s', request.user.username, group.id)
        raise PermissionDenied('You do not have permission to view this group.')

    try:
        # Prefetch members to avoid N+1 queries
        members = group.members.all().order_by('username')
        is_owner = group.is_owner(request.user)
    except DatabaseError as e:
        logger.error('Database error retrieving group %s details: %s', group.id, e)
        messages.error(request, 'An error occurred while loading group details.')
        return redirect('group_list')

    return render(request, 'calendar_app/group_detail.html', {
        'group': group,
        'members': members,
        'is_owner': is_owner,
    })


@login_required
def group_calendar_view(request, group_id):
    """
    Main view for group calendar handling all form submissions.

    Similar to personal calendar but for group shared calendars.
    Handles multiple POST actions:
    - submit_unavailability: Creates new group unavailability entries
    - show_free_times: Calculates available time slots for group on a date
    - show_last_five: Displays the 5 most recent group unavailability entries
    - delete_selected: Deletes selected entries (only creator can delete their entries)

    Free time slots are calculated based on ALL group members' unavailability.

    Args:
        request: HttpRequest object containing metadata about the request.
        group_id: Primary key of the group calendar to display.

    Returns:
        HttpResponse: Rendered group calendar template with forms and optionally
            free_times list if show_free_times was requested.

    Redirects:
        - After successful unavailability submission
        - After successful deletion of entries

    Raises:
        Http404: If group doesn't exist or user is not a member.
    """
    group = get_object_or_404(Group, id=group_id)

    # Check if user is a member
    if not group.is_member(request.user) and not group.is_owner(request.user):
        messages.error(request, 'You do not have permission to view this group calendar.')
        return redirect('group_list')

    free_times = None
    form_delete = None

    if request.method == 'POST':
        if 'submit_unavailability' in request.POST:
            form = GroupUnavailabilityForm(request.POST, submit_type='submit_unavailability')
            if form.is_valid():
                # Save but don't commit yet - need to associate with user and group
                new_record = form.save(commit=False)
                new_record.user = request.user
                new_record.group = group
                new_record.save()

                description_text = f' - {new_record.description}' if new_record.description else ''
                messages.success(
                    request,
                    f'New Record Made: <br>{new_record.date} from '
                    f'{new_record.start_time} to {new_record.end_time}{description_text}'
                )
                return redirect('group_calendar', group_id=group.id)
            print("Group Unavailability Form Errors:", form.errors)

        elif 'show_free_times' in request.POST:
            form = GroupUnavailabilityForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                selected_date = data['date']
                # Get ALL group unavailability entries for this date
                # Use select_related to fetch user data in one query (avoid N+1)
                unavail_list = GroupUnavailability.objects.filter(
                    group=group,
                    date=selected_date
                ).select_related('user')

                start_dt = datetime.datetime.combine(selected_date, datetime.time(8, 0))
                end_dt = datetime.datetime.combine(selected_date, datetime.time(20, 0))
                all_slots = []
                while start_dt < end_dt:
                    all_slots.append(start_dt.time())
                    start_dt += datetime.timedelta(minutes=30)

                # Mark taken slots
                taken_slots = set()
                for unavail in unavail_list:
                    current_slot = datetime.datetime.combine(selected_date, unavail.start_time)
                    unavail_end = datetime.datetime.combine(selected_date, unavail.end_time)
                    while current_slot < unavail_end:
                        taken_slots.add(current_slot.time())
                        current_slot += datetime.timedelta(minutes=30)

                # Calculate free times
                free_times = [slot.strftime("%H:%M") for slot in all_slots
                              if slot not in taken_slots]
            print("Show Free Times Form Errors:", form.errors)
            form_delete = GroupDeleteSelectedForm()

        elif 'show_last_five' in request.POST:
            form = GroupUnavailabilityForm()
            # Get last five entries for this group
            # Use select_related to optimize user data fetching
            last_five = GroupUnavailability.objects.filter(group=group).select_related('user').order_by('-id')[:5]
            choices = []
            for entry in last_five:
                # Include username in label so users know who created it
                description_text = f' - {entry.description}' if entry.description else ''
                label = (f"{entry.user.username}: {entry.date} from "
                        f"{entry.start_time} to {entry.end_time}{description_text}")
                # Only allow deletion of own entries - we'll enforce this in the view
                choices.append((entry.id, label))
            form_delete = GroupDeleteSelectedForm()
            form_delete.fields['entry_ids'].choices = choices

        elif 'delete_selected' in request.POST:
            form = GroupUnavailabilityForm()
            # Repopulate choices from the last five entries
            # Use select_related to optimize user data fetching
            last_five = GroupUnavailability.objects.filter(group=group).select_related('user').order_by('-id')[:5]
            choices = []
            for entry in last_five:
                description_text = f' - {entry.description}' if entry.description else ''
                label = (f"{entry.user.username}: {entry.date} from "
                        f"{entry.start_time} to {entry.end_time}{description_text}")
                choices.append((entry.id, label))

            form_delete = GroupDeleteSelectedForm(request.POST)
            form_delete.fields['entry_ids'].choices = choices

            if form_delete.is_valid():
                entry_ids = form_delete.cleaned_data['entry_ids']
                print("Delete form cleaned data:", entry_ids)
                if entry_ids:
                    entry_ids = [int(e_id) for e_id in entry_ids]
                    # CRITICAL: Only delete entries created by current user
                    count_before = GroupUnavailability.objects.filter(
                        group=group, user=request.user, id__in=entry_ids).count()
                    print("Count before deletion:", count_before)
                    GroupUnavailability.objects.filter(
                        group=group, user=request.user, id__in=entry_ids).delete()
                    count_after = GroupUnavailability.objects.filter(
                        group=group, user=request.user, id__in=entry_ids).count()
                    print("Count after deletion:", count_after)

                    if count_before > 0:
                        messages.success(request, f'Deleted {count_before} entry(ies).')
                    else:
                        messages.warning(request, 'No entries deleted. You can only delete your own entries.')
                else:
                    print("No entries selected for deletion.")
                return redirect('group_calendar', group_id=group.id)
            print("Delete Form Errors:", form_delete.errors)
        else:
            form = GroupUnavailabilityForm()
            form_delete = GroupDeleteSelectedForm()
    else:
        form = GroupUnavailabilityForm()
        form_delete = GroupDeleteSelectedForm()

    return render(request, 'calendar_app/group_calendar.html', {
        'form': form,
        'form_delete': form_delete,
        'free_times': free_times,
        'group': group,
    })


@login_required
def group_add_member_view(request, group_id):
    """
    Add a member to a group by username (owner only).

    Handles adding new members to a group. Only the group owner can add members.
    Prevents adding users who are already members.

    Args:
        request: HttpRequest object containing metadata about the request.
        group_id: Primary key of the group to add member to.

    Returns:
        HttpResponse: Rendered add member template or redirect to group detail.

    Redirects:
        - After successful member addition to group detail view
        - If user is not owner to group detail view

    Raises:
        Http404: If group doesn't exist.
    """
    group = get_object_or_404(Group, id=group_id)

    # Check if user is the owner (explicit permission check)
    if not group.is_owner(request.user):
        logger.warning(
            'Permission denied: User %s attempted to add member to group %s',
            request.user.username, group.id
        )
        raise PermissionDenied('Only the group owner can add members.')

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user_to_add = User.objects.get(username=username)

            # Check if user is already a member
            if group.is_member(user_to_add):
                messages.warning(request, f'{username} is already a member of this group.')
            else:
                group.members.add(user_to_add)
                messages.success(request, f'{username} added to group successfully!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = AddMemberForm()

    return render(request, 'calendar_app/group_add_member.html', {
        'form': form,
        'group': group,
    })


@login_required
def group_remove_member_view(request, group_id, user_id):
    """
    Remove a member from a group (owner only).

    Allows the group owner to remove members from the group.
    Cannot remove the owner themselves.

    Args:
        request: HttpRequest object containing metadata about the request.
        group_id: Primary key of the group.
        user_id: Primary key of the user to remove.

    Returns:
        HttpResponse: Redirect to group detail view.

    Raises:
        Http404: If group or user doesn't exist.
    """
    group = get_object_or_404(Group, id=group_id)
    user_to_remove = get_object_or_404(User, id=user_id)

    # Check if user is the owner (explicit permission check)
    if not group.is_owner(request.user):
        logger.warning(
            'Permission denied: User %s attempted to remove member from group %s',
            request.user.username, group.id
        )
        raise PermissionDenied('Only the group owner can remove members.')

    # Cannot remove the owner
    if user_to_remove == group.created_by:
        messages.error(request, 'Cannot remove the group owner.')
        return redirect('group_detail', group_id=group.id)

    # Remove the member
    group.members.remove(user_to_remove)
    messages.success(request, f'{user_to_remove.username} removed from group.')

    return redirect('group_detail', group_id=group.id)


@login_required
def group_delete_view(request, group_id):
    """
    Delete a group (owner only).

    Allows the group owner to permanently delete a group and all associated
    group unavailability entries (cascade delete).

    Args:
        request: HttpRequest object containing metadata about the request.
        group_id: Primary key of the group to delete.

    Returns:
        HttpResponse: Rendered delete confirmation template or redirect to group list.

    Redirects:
        - After successful deletion to group list view
        - If user is not owner to group detail view

    Raises:
        Http404: If group doesn't exist.
    """
    group = get_object_or_404(Group, id=group_id)

    # Check if user is the owner (explicit permission check)
    if not group.is_owner(request.user):
        logger.warning('Permission denied: User %s attempted to delete group %s', request.user.username, group.id)
        raise PermissionDenied('Only the group owner can delete this group.')

    if request.method == 'POST':
        group_name = group.name
        group.delete()  # Cascade deletes all GroupUnavailability entries
        messages.success(request, f'Group "{group_name}" deleted successfully.')
        return redirect('group_list')

    return render(request, 'calendar_app/group_delete.html', {
        'group': group,
    })
