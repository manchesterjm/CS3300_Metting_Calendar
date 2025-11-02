"""
Django forms for the calendar application.

This module defines forms for managing unavailability entries, including
creation, validation, and deletion of time periods when users are unavailable
for meetings.
"""
import datetime

from django import forms
from .models import Unavailability


class UnavailabilityForm(forms.ModelForm):
    """
    Form for creating and displaying unavailability entries.

    This form handles the creation of new unavailability entries with automatic
    date defaulting to today's date. It includes conditional validation based
    on the submit_type parameter to prevent invalid entries when creating new
    unavailability records.

    Args:
        submit_type (str, optional): Type of form submission ('submit_unavailability'
            enables strict validation). Defaults to None.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the UnavailabilityForm with custom default values.

        Sets the date field default to today's date and configures widget
        attributes for proper browser display.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. May include 'submit_type'
                which is popped before calling super().__init__().
        """
        # Pop the submit_type keyword if provided (used for conditional validation)
        self.submit_type = kwargs.pop('submit_type', None)
        super().__init__(*args, **kwargs)
        # Set the default date to today's date
        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d')
        self.fields['date'].initial = today
        # Update the widget value attribute so the browser shows today's date
        self.fields['date'].widget.attrs.update({'value': today_str})

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
        """
        Validate form data with conditional checks based on submit_type.

        When submit_type is 'submit_unavailability', performs additional validation
        to ensure users have changed default values before submission to prevent
        database corruption from unintentional default entries.

        Returns:
            dict: The cleaned data dictionary from form validation.

        Raises:
            ValidationError: If required fields still contain default values when
                submitting a new unavailability entry.
        """
        cleaned_data = super().clean()
        # Only perform default-check validation when submitting new unavailability
        if self.submit_type == 'submit_unavailability':
            # Check against fake default values to ensure user changed inputs
            # Not strictly needed with dynamic date default, but kept for flexibility
            fake_default_date = datetime.date(2025, 1, 1)
            fake_default_time = datetime.time(0, 0)
            date = cleaned_data.get('date')
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')
            # Validate that user changed date and times from defaults
            if date == fake_default_date:
                self.add_error('date', "Please select a valid date.")
            if start_time == fake_default_time:
                self.add_error('start_time', "Please select a valid start time.")
            if end_time == fake_default_time:
                self.add_error('end_time', "Please select a valid end time.")
        return cleaned_data


class DeleteSelectedForm(forms.Form):
    """
    Form for selecting multiple unavailability entries for deletion.

    This form provides checkboxes for selecting one or more unavailability
    entries to delete. The choices are populated dynamically in the view
    based on the last five entries in the database.

    Attributes:
        entry_ids: Multiple choice field containing entry IDs for deletion.
            Uses checkboxes for user-friendly multi-selection.
    """
    entry_ids = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
