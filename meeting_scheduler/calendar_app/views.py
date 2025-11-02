"""
Django views for the calendar application.

This module contains the main view logic for the meeting scheduler,
including handling unavailability entry creation, free time slot calculation,
entry display, and deletion functionality.

Main View:
    - calendar_view: Handles all calendar operations (add, delete, show free times)

TODO: Consider adding timezone support for international users.
TODO: Optimize free time calculation with database-level queries.

Version: 2.0
Security: All views require authentication and implement CSRF protection
"""
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UnavailabilityForm, DeleteSelectedForm
from .models import Unavailability
from .utils import calculate_free_time_slots


@login_required
def home_view(request):
    """
    Landing page view for authenticated users.

    Displays a user-friendly dashboard with quick access to main features:
    - View/manage groups
    - Create new groups
    - Access account settings

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered home template.
    """
    return render(request, 'calendar_app/home.html')


@login_required
def calendar_view(request):
    """
    Main view for the calendar application handling all form submissions.

    This single view handles multiple POST actions using a button name pattern:
    - submit_unavailability: Creates new unavailability entries
    - show_free_times: Calculates and displays available time slots for a date
    - show_last_five: Displays the 5 most recent unavailability entries
    - delete_selected: Deletes selected unavailability entries

    Free time slots are calculated in 30-minute intervals between 8:00-20:00,
    excluding any periods marked as unavailable in the database.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered calendar template with form(s) and optionally
            free_times list if show_free_times was requested.

    Redirects:
        - After successful unavailability submission
        - After successful deletion of entries
    """
    free_times = None
    form_delete = None  # This will be used for deletion

    if request.method == 'POST':
        if 'submit_unavailability' in request.POST:
            form = UnavailabilityForm(request.POST, submit_type='submit_unavailability')
            if form.is_valid():
                # Save but don't commit yet - need to associate with user
                new_record = form.save(commit=False)
                new_record.user = request.user
                new_record.save()
                # Success message with description if provided
                if new_record.description:
                    messages.success(
                        request,
                        f'New Record Made: <br>{new_record.date} from '
                        f'{new_record.start_time} to {new_record.end_time} - {new_record.description}'
                    )
                else:
                    messages.success(
                        request,
                        f'New Record Made: <br>{new_record.date} from '
                        f'{new_record.start_time} to {new_record.end_time}'
                    )
                return redirect('calendar')  # return to calendar initial view
            # and again, I have not been able to make it error in such a way
            # that this gets displayed now
            print("Unavailability Form Errors:", form.errors)

        elif 'show_free_times' in request.POST:
            # For showing free times in personal calendar, check only current user's unavailability
            # (Group calendars show all members - see group_calendar_view in group_views.py)
            selected_date_str = request.POST.get('date')
            try:
                selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                # Check only current user's unavailability for personal calendar privacy
                unavail_list = Unavailability.objects.filter(date=selected_date, user=request.user)

                # Calculate free time slots using utility function
                free_times = calculate_free_time_slots(selected_date, unavail_list)

                # Recreate form with the selected date for display
                form = UnavailabilityForm(initial={'date': selected_date})
            except (ValueError, TypeError):
                # If date parsing fails, show error
                messages.error(request, 'Please select a valid date.')
                form = UnavailabilityForm()

            form_delete = DeleteSelectedForm()  # Initialize an empty deletion form for display

        # show last five entries in the database
        elif 'show_last_five' in request.POST:
            form = UnavailabilityForm()
            last_five = Unavailability.objects.filter(user=request.user).order_by('-id')[:5]
            choices = []
            for entry in last_five:  # start the print out here
                # Format: Date from Time to Time - Description (if provided)
                if entry.description:
                    label = f"{entry.date} from {entry.start_time} to {entry.end_time} - {entry.description}"
                else:
                    label = f"{entry.date} from {entry.start_time} to {entry.end_time}"
                choices.append((entry.id, label))
            form_delete = DeleteSelectedForm()
            # what entries are we going to delete, entry ids are used to find
            # the entries in the DB
            form_delete.fields['entry_ids'].choices = choices

        elif 'delete_selected' in request.POST:
            form = UnavailabilityForm()  # Reinitialize the main form
            # Repopulate choices from the last five entries
            last_five = Unavailability.objects.filter(user=request.user).order_by('-id')[:5]
            choices = []  # list/array of the entries we selected
            for entry in last_five:
                # Format: Date from Time to Time - Description (if provided)
                if entry.description:
                    label = f"{entry.date} from {entry.start_time} to {entry.end_time} - {entry.description}"
                else:
                    label = f"{entry.date} from {entry.start_time} to {entry.end_time}"
                choices.append((entry.id, label))

            form_delete = DeleteSelectedForm(request.POST)
            form_delete.fields['entry_ids'].choices = choices

            if form_delete.is_valid():
                entry_ids = form_delete.cleaned_data['entry_ids']
                # Debug output, I left this in to show what I did to catch errors,
                # but it should not be needed anymore. It may be good for future devs.
                print("Delete form cleaned data:", entry_ids)
                if entry_ids:
                    entry_ids = [int(e_id) for e_id in entry_ids]
                    # Only delete entries belonging to the current user
                    count_before = Unavailability.objects.filter(
                        user=request.user, id__in=entry_ids).count()
                    print("Count before deletion:", count_before)
                    Unavailability.objects.filter(user=request.user, id__in=entry_ids).delete()
                    count_after = Unavailability.objects.filter(
                        user=request.user, id__in=entry_ids).count()
                    print("Count after deletion:", count_after)
                else:
                    print("No entries selected for deletion.")  # we didn't select anything
                return redirect('calendar')  # return to calendar initial view
            # added this as a catch all, but I can't make it error in a way
            # that this gets displayed now
            print("Delete Form Errors:", form_delete.errors)
        else:
            form = UnavailabilityForm()
            form_delete = DeleteSelectedForm()
    else:
        form = UnavailabilityForm()
        form_delete = DeleteSelectedForm()

    return render(request, 'calendar_app/calendar.html', {
        'form': form,
        'form_delete': form_delete,
        'free_times': free_times,
    })
