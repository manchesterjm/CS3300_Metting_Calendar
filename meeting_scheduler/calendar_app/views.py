# calendar_app/views.py
import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UnavailabilityForm, DeleteSelectedForm
from .models import Unavailability

def calendar_view(request):
    free_times = None
    form_delete = None  # This will be used for deletion

    if request.method == 'POST':
        if 'submit_unavailability' in request.POST:
            form = UnavailabilityForm(request.POST, submit_type='submit_unavailability')
            if form.is_valid():
                # biggest pain was this part, getting an entry to save properly into the DB
                new_record = form.save()
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
            form = UnavailabilityForm(request.POST)
            # it is always good to check if the form is valid.  If not, the DB
            # did corrupt a few times, which is why I needed to add this form to
            # delete past entries.  It now serves to delete a bad entry that a user
            # might make
            if form.is_valid():
                data = form.cleaned_data
                selected_date = data['date']
                unavail_list = Unavailability.objects.filter(date=selected_date)

                start_dt = datetime.datetime.combine(selected_date, datetime.time(8, 0))
                end_dt = datetime.datetime.combine(selected_date, datetime.time(20, 0))
                all_slots = []
                while start_dt < end_dt:
                    all_slots.append(start_dt.time())
                    start_dt += datetime.timedelta(minutes=30)
                # start date and time display
                taken_slots = set()
                for unavail in unavail_list:
                    current_slot = datetime.datetime.combine(selected_date, unavail.start_time)
                    unavail_end = datetime.datetime.combine(selected_date, unavail.end_time)
                    while current_slot < unavail_end:
                        taken_slots.add(current_slot.time())
                        current_slot += datetime.timedelta(minutes=30)
                # actual print out
                free_times = [slot.strftime("%H:%M") for slot in all_slots
                              if slot not in taken_slots]
            # I didn't do this to start and I found out that it didn't work
            # if the database corrupted
            print("Show Free Times Form Errors:", form.errors)
            form_delete = DeleteSelectedForm()  # Initialize an empty deletion form for display

        # show last five entries in the database
        elif 'show_last_five' in request.POST:
            form = UnavailabilityForm()
            last_five = Unavailability.objects.order_by('-id')[:5]
            choices = []
            for entry in last_five:  # start the print out here
                label = f"{entry.date} from {entry.start_time} to {entry.end_time}"
                choices.append((entry.id, label))
            form_delete = DeleteSelectedForm()
            # what entries are we going to delete, entry ids are used to find
            # the entries in the DB
            form_delete.fields['entry_ids'].choices = choices

        elif 'delete_selected' in request.POST:
            form = UnavailabilityForm()  # Reinitialize the main form
            # Repopulate choices from the last five entries
            last_five = Unavailability.objects.order_by('-id')[:5]
            choices = []  # list/array of the entries we selected
            for entry in last_five:
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
                    count_before = Unavailability.objects.filter(
                        id__in=entry_ids).count()
                    print("Count before deletion:", count_before)
                    Unavailability.objects.filter(id__in=entry_ids).delete()
                    count_after = Unavailability.objects.filter(
                        id__in=entry_ids).count()
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
