# calendar_app/forms.py
# most of this file was updated from a template
# I changed it to do what I wanted using django documentation
# and course material from CS 2080
# I also used ChatGPT to help me troubleshoot code syntax

import datetime

from django import forms
from .models import Unavailability

class UnavailabilityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Pop the submit_type keyword if provided (used for conditional validation)
        self.submit_type = kwargs.pop('submit_type', None)
        super().__init__(*args, **kwargs)
        ### set the defulat date to today's date ###
        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d') #grab year month day
        self.fields['date'].initial = today # set date in our meta initial to that date
        # update the widget value attr so the browser shows today's date
        self.fields['date'].widget.attrs.update({'value': today_str})
        ### end set default date to today's date ###

    class Meta:
        model = Unavailability
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'start_time': forms.TimeInput(
                attrs={'type': 'time', 'value': '00:00'}
            ),
            'end_time': forms.TimeInput(
                attrs={'type': 'time', 'value': '00:00'}
            ),
        }
        initial = {
            # if a static initial date is required, place it here and then comment out
            # the code above that sets the date to the current date
            'start_time': datetime.time(0, 0),
            'end_time': datetime.time(0, 0),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Only perform default-check validation when submitting new unavailability.
        if self.submit_type == 'submit_unavailability':
            # need these fake dates to check against the user input data to make sure
            # they changed the time and date from default
            # not really needed now as I am getting the current date as default, but
            # I left it here in case a static date is required
            fake_default_date = datetime.date(2025, 1, 1)
            fake_default_time = datetime.time(0, 0) # midnight
            date = cleaned_data.get('date')
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')
            ### start checking if the user changed the date and time so the database will not corrupt
            if date == fake_default_date:
                self.add_error('date', "Please select a valid date.")
            if start_time == fake_default_time:
                self.add_error('start_time', "Please select a valid start time.")
            if end_time == fake_default_time:
                self.add_error('end_time', "Please select a valid end time.")
            ### end checking ###
        return cleaned_data

class DeleteSelectedForm(forms.Form):
    # Form for selecting multiple Unavailability entries for deletion.
    # The choices will be populated dynamically in the view.
    entry_ids = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
