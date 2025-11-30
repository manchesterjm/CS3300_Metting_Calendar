"""
Django views for the calendar application.

This module contains view logic for the meeting scheduler following SOFA principles:
- Single Responsibility: Each view handles one specific action
- Open/Closed: Views can be extended through composition
- Functional Composition: Complex operations delegated to service layer
- Abstraction: Business logic abstracted to services.py

Views:
    - calendar_view: Main router view delegating to action handlers
    - Action handlers: Focused functions for each POST action

Version: 3.0 - Refactored with service layer
Security: All views require authentication and implement CSRF protection
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from .forms import UnavailabilityForm, DeleteSelectedForm
from .services import TimeSlotService, UnavailabilityService


# Action handler functions (Single Responsibility)

def _handle_submit_unavailability(request: HttpRequest) -> tuple:
    """
    Handle creation of new unavailability record.

    Args:
        request: HTTP request with POST data

    Returns:
        Tuple of (should_redirect, form, form_delete, free_times)
    """
    form = UnavailabilityForm(request.POST, submit_type='submit_unavailability')

    if form.is_valid():
        # Save through the form (which handles recurring logic)
        new_record = form.save(commit=False)
        new_record.user = request.user
        new_record.save()

        messages.success(
            request,
            f'New Record Made: <br>{new_record.date} from '
            f'{new_record.start_time} to {new_record.end_time}'
        )
        return True, None, None, None

    # Form invalid - return for display
    return False, form, DeleteSelectedForm(), None


def _handle_show_free_times(request: HttpRequest) -> tuple:
    """
    Calculate and display free time slots for selected date.

    Uses TimeSlotService to abstract business logic.

    Args:
        request: HTTP request with POST data

    Returns:
        Tuple of (should_redirect, form, form_delete, free_times)
    """
    form = UnavailabilityForm(request.POST)

    if form.is_valid():
        selected_date = form.cleaned_data['date']

        # Delegate to service layer (Abstraction principle)
        free_times = TimeSlotService.calculate_free_slots(
            user=request.user,
            date=selected_date
        )

        return False, form, DeleteSelectedForm(), free_times

    # Form invalid
    return False, form, DeleteSelectedForm(), None


def _handle_show_last_five(request: HttpRequest) -> tuple:
    """
    Display last 5 unavailability entries for deletion selection.

    Uses UnavailabilityService for data access.

    Args:
        request: HTTP request

    Returns:
        Tuple of (should_redirect, form, form_delete, free_times)
    """
    form = UnavailabilityForm()

    # Delegate to service layer
    choices = UnavailabilityService.get_recent_entries(
        user=request.user,
        limit=5
    )

    form_delete = DeleteSelectedForm()
    form_delete.fields['entry_ids'].choices = choices

    return False, form, form_delete, None


def _handle_delete_selected(request: HttpRequest) -> tuple:
    """
    Delete selected unavailability entries.

    Uses UnavailabilityService for data operations.

    Args:
        request: HTTP request with POST data

    Returns:
        Tuple of (should_redirect, form, form_delete, free_times)
    """
    form = UnavailabilityForm()

    # Get choices for form validation
    choices = UnavailabilityService.get_recent_entries(
        user=request.user,
        limit=5
    )

    form_delete = DeleteSelectedForm(request.POST)
    form_delete.fields['entry_ids'].choices = choices

    if form_delete.is_valid():
        entry_ids = form_delete.cleaned_data['entry_ids']

        if entry_ids:
            entry_ids = [int(e_id) for e_id in entry_ids]

            # Delegate to service layer
            deleted_count = UnavailabilityService.delete_entries(
                user=request.user,
                entry_ids=entry_ids
            )

            if deleted_count > 0:
                messages.success(request, f'Deleted {deleted_count} entry(ies)')

        return True, None, None, None

    # Form invalid
    return False, form, form_delete, None


# Main view (Router pattern - delegates to handlers)

@login_required
def calendar_view(request: HttpRequest) -> HttpResponse:
    """
    Main calendar view acting as a router to action handlers.

    Follows Single Responsibility: Only routes requests to appropriate handlers.
    All business logic delegated to service layer and action handlers.

    POST Actions:
        - submit_unavailability: Create new entry
        - show_free_times: Calculate available slots
        - show_last_five: Show recent entries for deletion
        - delete_selected: Delete selected entries

    Args:
        request: HttpRequest object

    Returns:
        HttpResponse: Rendered template or redirect
    """
    free_times = None
    form = None
    form_delete = None

    if request.method == 'POST':
        # Route to appropriate handler (Open/Closed principle - easy to extend)
        if 'submit_unavailability' in request.POST:
            should_redirect, form, form_delete, free_times = \
                _handle_submit_unavailability(request)

        elif 'show_free_times' in request.POST:
            should_redirect, form, form_delete, free_times = \
                _handle_show_free_times(request)

        elif 'show_last_five' in request.POST:
            should_redirect, form, form_delete, free_times = \
                _handle_show_last_five(request)

        elif 'delete_selected' in request.POST:
            should_redirect, form, form_delete, free_times = \
                _handle_delete_selected(request)

        else:
            # Unknown action
            form = UnavailabilityForm()
            form_delete = DeleteSelectedForm()
            should_redirect = False

        # Handle redirect if needed
        if should_redirect:
            return redirect('calendar')

    # GET request or POST without redirect
    if form is None:
        form = UnavailabilityForm()
    if form_delete is None:
        form_delete = DeleteSelectedForm()

    return render(request, 'calendar_app/calendar.html', {
        'form': form,
        'form_delete': form_delete,
        'free_times': free_times,
    })
