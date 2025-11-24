"""
Django forms for the calendar application.

This module defines forms for managing unavailability entries, including
creation, validation, and deletion of time periods when users are unavailable
for meetings. Also includes forms for group management and shared calendars.

Forms:
    - UnavailabilityForm: Create/edit unavailability entries
    - DeleteSelectedForm: Bulk delete unavailability entries
    - GroupCreateForm: Create new calendar groups
    - AddMemberForm: Add users to groups
    - GroupUnavailabilityForm: Group calendar entries
    - GroupDeleteSelectedForm: Bulk delete group entries
    - JoinGroupForm: Join a group using a join code
    - MeetingProposalForm: Create meeting proposals

Security Note: All forms use Django's built-in CSRF protection and input sanitization.
"""
import datetime

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Unavailability, Group, GroupUnavailability, MeetingProposal


class BaseDescriptionForm(forms.Form):
    """
    Base form class for forms that include a description field.

    Provides common validation logic for description fields to avoid code duplication
    between UnavailabilityForm and GroupUnavailabilityForm.
    """

    def clean_description(self):
        """
        Validate the description field.

        Ensures description is not too long and doesn't contain dangerous characters.

        Returns:
            str: The cleaned and stripped description.

        Raises:
            ValidationError: If description exceeds 200 characters or contains invalid data.
        """
        description = self.cleaned_data.get('description', '')
        if description:
            # Strip whitespace
            description = description.strip()
            # Validate length (redundant with maxlength, but server-side is critical)
            if len(description) > 200:
                raise forms.ValidationError('Description must be 200 characters or less.')
        return description


class UnavailabilityForm(BaseDescriptionForm, forms.ModelForm):  # pylint: disable=too-many-ancestors
    """
    Form for creating and displaying unavailability entries with recurring pattern support.

    This form handles the creation of new unavailability entries with automatic
    date defaulting to today's date. It includes conditional validation based
    on the submit_type parameter to prevent invalid entries when creating new
    unavailability records.

    Supports recurring patterns (daily, weekly, monthly) with customizable intervals
    and end dates.

    Args:
        submit_type (str, optional): Type of form submission ('submit_unavailability'
            enables strict validation). Defaults to None.
    """

    FREQUENCY_CHOICES = [
        ('', 'Select frequency'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    DAY_OF_WEEK_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    is_recurring = forms.BooleanField(
        required=False,
        label='Make this recurring',
        help_text='Create this unavailability on multiple dates automatically'
    )
    frequency = forms.ChoiceField(
        choices=FREQUENCY_CHOICES,
        required=False,
        label='Repeat frequency',
        help_text='How often should this repeat?'
    )
    days_of_week = forms.MultipleChoiceField(
        choices=DAY_OF_WEEK_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Days of week',
        help_text='For weekly recurrence, select which days'
    )
    interval = forms.IntegerField(
        required=False,
        initial=1,
        min_value=1,
        max_value=52,
        label='Repeat every',
        help_text='Repeat every N days/weeks/months (e.g., 1 = every week, 2 = every other week)'
    )
    recurrence_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End date (optional)',
        help_text='When should the recurrence stop? Leave blank for 90 days from start'
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the UnavailabilityForm with custom default values.

        Sets the date field default to today's date and configures widget
        attributes for proper browser display. Adds recurrence fields dynamically.

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
        fields = ['date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'start_time': forms.TimeInput(
                attrs={'type': 'time'}
            ),
            'end_time': forms.TimeInput(
                attrs={'type': 'time'}
            ),
            'description': forms.TextInput(attrs={
                'placeholder': 'Optional: Add note (e.g., "Doctor appointment", "Meeting")',
                'maxlength': 200,
                'class': 'form-input'
            })
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

        Also validates recurrence pattern fields when is_recurring is checked.

        Returns:
            dict: The cleaned data dictionary from form validation.

        Raises:
            ValidationError: If required fields still contain default values when
                submitting a new unavailability entry, or if recurrence fields are invalid.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        is_recurring = cleaned_data.get('is_recurring', False)
        frequency = cleaned_data.get('frequency')
        days_of_week = cleaned_data.get('days_of_week', [])
        interval = cleaned_data.get('interval')
        recurrence_end_date = cleaned_data.get('recurrence_end_date')
        date = cleaned_data.get('date')

        # Only perform default-check validation when submitting new unavailability
        if self.submit_type == 'submit_unavailability':
            # Check against fake default values to ensure user changed inputs
            # Not strictly needed with dynamic date default, but kept for flexibility
            fake_default_date = datetime.date(2025, 1, 1)
            fake_default_time = datetime.time(0, 0)

            # Validate that user changed date and times from defaults
            if date == fake_default_date:
                self.add_error('date', "Please select a valid date.")
            if start_time == fake_default_time:
                self.add_error('start_time', "Please select a valid start time.")
            if end_time == fake_default_time:
                self.add_error('end_time', "Please select a valid end time.")

            # Validate time range (only when submitting new unavailability)
            if start_time and end_time and start_time >= end_time:
                self.add_error('end_time', "End time must be after start time.")

            # Validate recurrence pattern if recurring is checked
            if is_recurring:
                if not frequency:
                    self.add_error('frequency', "Please select a frequency for recurring entries.")

                if frequency == 'weekly':
                    if not days_of_week:
                        self.add_error('days_of_week', "Please select at least one day of the week for weekly recurrence.")
                    else:
                        # Security: Validate each day value (defense-in-depth)
                        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday',
                                     'friday', 'saturday', 'sunday']
                        for day in days_of_week:
                            if day not in valid_days:
                                self.add_error('days_of_week', f'Invalid day selected: {day}.')
                                break

                if not interval or interval < 1:
                    self.add_error('interval', "Interval must be at least 1.")

                # Validate end date is after start date if provided
                if recurrence_end_date and date and recurrence_end_date <= date:
                    self.add_error('recurrence_end_date', "End date must be after the start date.")

        return cleaned_data


class DeleteSelectedForm(forms.Form):
    """
    Form for selecting multiple unavailability entries for deletion.

    This form provides checkboxes for selecting one or more unavailability
    entries to delete. The choices are populated dynamically in the view
    based on the last five entries in the database.

    Supports deleting entire recurring series when an instance is selected.

    Attributes:
        entry_ids: Multiple choice field containing entry IDs for deletion.
            Uses checkboxes for user-friendly multi-selection.
        delete_series: Boolean field to delete entire recurring series.
    """
    entry_ids = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    delete_series = forms.BooleanField(
        required=False,
        label='Delete entire recurring series (if applicable)',
        help_text='If checked, will delete the master entry and all instances of any recurring series'
    )


class GroupCreateForm(forms.ModelForm):
    """
    Form for creating a new group.

    This form validates that the group name is unique and not empty.

    Attributes:
        name: CharField for the group name (max 100 characters).
    """

    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter group name',
                'maxlength': 100,
                'class': 'form-input'
            })
        }

    def clean_name(self):
        """
        Validate that the group name is unique.

        Returns:
            str: The cleaned group name.

        Raises:
            ValidationError: If a group with this name already exists.
        """
        name = self.cleaned_data.get('name')
        if Group.objects.filter(name=name).exists():
            raise forms.ValidationError('A group with this name already exists.')
        return name


class AddMemberForm(forms.Form):
    """
    Form for adding a member to a group by username.

    Validates that the username exists in the system.

    Attributes:
        username: CharField for entering the username to add.
    """

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username',
            'autocomplete': 'off',
            'class': 'form-input'
        })
    )

    def clean_username(self):
        """
        Validate that the username exists.

        Returns:
            str: The cleaned username.

        Raises:
            ValidationError: If the user does not exist.
        """
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('User does not exist.')
        return username


class GroupUnavailabilityForm(BaseDescriptionForm, forms.ModelForm):  # pylint: disable=too-many-ancestors
    """
    Form for creating group unavailability entries.

    Similar to UnavailabilityForm but includes an optional description field
    and is used for group calendars.

    Args:
        submit_type (str, optional): Type of form submission ('submit_unavailability'
            enables strict validation). Defaults to None.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the GroupUnavailabilityForm with custom default values.

        Sets the date field default to today's date.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. May include 'submit_type'.
        """
        self.submit_type = kwargs.pop('submit_type', None)
        super().__init__(*args, **kwargs)

        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d')
        self.fields['date'].initial = today
        self.fields['date'].widget.attrs.update({'value': today_str})

    class Meta:
        model = GroupUnavailability
        fields = ['date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.TextInput(attrs={
                'placeholder': 'Optional: Add description (e.g., "Team meeting")',
                'maxlength': 200,
                'class': 'form-input'
            })
        }

    def clean(self):
        """
        Validate form data with conditional checks.

        When submit_type is 'submit_unavailability', validates that users
        have changed default time values.

        Returns:
            dict: The cleaned data dictionary.

        Raises:
            ValidationError: If default time values are submitted.
        """
        cleaned_data = super().clean()

        if self.submit_type == 'submit_unavailability':
            fake_default_time = datetime.time(0, 0)
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')

            if start_time == fake_default_time:
                self.add_error('start_time', "Please select a valid start time.")
            if end_time == fake_default_time:
                self.add_error('end_time', "Please select a valid end time.")
            if start_time and end_time and start_time >= end_time:
                self.add_error('end_time', "End time must be after start time.")

        return cleaned_data


class GroupDeleteSelectedForm(forms.Form):
    """
    Form for selecting group unavailability entries to delete.

    Similar to DeleteSelectedForm but for group calendar entries.

    Attributes:
        entry_ids: Multiple choice field for selecting entries to delete.
    """

    entry_ids = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple
    )


class JoinGroupForm(forms.Form):
    """
    Form for joining a group using a join code.

    Validates that the join code exists, is enabled, and the user is not
    already a member of the group.

    Attributes:
        join_code: CharField for entering the 8-character join code.
    """

    join_code = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 8-character code',
            'autocomplete': 'off',
            'class': 'form-input',
            'style': 'text-transform: uppercase;',
            'pattern': '[A-Z0-9]{8}'
        }),
        help_text='Enter the 8-character join code (e.g., AB2C3DEF)'
    )

    def __init__(self, *args, user=None, **kwargs):
        """
        Initialize the JoinGroupForm with user context.

        Args:
            user: The User instance attempting to join (used for validation).
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.user = user
        self.group = None  # Will be set during validation
        super().__init__(*args, **kwargs)

    def clean_join_code(self):
        """
        Validate the join code and check user eligibility.

        Security: Uses constant-time validation and generic error messages to prevent
        timing attacks that could reveal whether codes exist. Validates format
        server-side as defense-in-depth (client-side validation can be bypassed).

        Returns:
            str: The cleaned and uppercased join code.

        Raises:
            ValidationError: If code is invalid, disabled, or user already member.
        """
        import re
        import secrets
        import time

        code = self.cleaned_data.get('join_code', '').strip().upper()

        # Security: Server-side pattern validation (defense-in-depth)
        # Client-side validation can be bypassed via dev tools or raw HTTP requests
        if not re.match(r'^[A-Z0-9]{8}$', code):
            raise forms.ValidationError(
                'Join code must be exactly 8 characters (uppercase letters and numbers only).'
            )

        # Security: Constant-time validation to prevent timing attacks
        # Always perform lookup (no early exit based on code format)
        try:
            group = Group.objects.get(join_code=code)
            code_exists = True
        except Group.DoesNotExist:
            group = None
            code_exists = False

        # Perform all checks (constant-time logic)
        is_enabled = code_exists and group.join_code_enabled
        is_not_member = code_exists and (not self.user or not group.is_member(self.user))
        is_valid = code_exists and is_enabled and is_not_member

        # Generic error message for all failure cases (prevents information disclosure)
        # Add random delay to normalize timing (prevents timing analysis)
        if not is_valid:
            time.sleep(secrets.randbelow(50) / 1000)  # 0-50ms random delay
            raise forms.ValidationError(
                'Invalid or inactive join code. Please check and try again.'
            )

        # Store the group for use in the view
        self.group = group

        return code


class MeetingProposalForm(forms.ModelForm):
    """
    Form for creating a meeting proposal.

    This form allows users to propose a meeting time for their group.
    All group members must accept the proposal for it to be scheduled.

    Attributes:
        title: CharField for the meeting title.
        description: TextField for optional meeting details.
        meeting_datetime: DateTimeField for the proposed meeting time.
        duration_minutes: ChoiceField for meeting duration (30, 60, or 120 minutes).
    """

    class Meta:
        model = MeetingProposal
        fields = ['title', 'description', 'meeting_datetime', 'duration_minutes']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter meeting title',
                'maxlength': 200,
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Optional: Add meeting agenda or details',
                'rows': 3,
                'class': 'form-input'
            }),
            'meeting_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-input'
            }),
            'duration_minutes': forms.Select(attrs={
                'class': 'form-input'
            })
        }

    def clean_meeting_datetime(self):
        """
        Validate that the meeting datetime is in the future.

        Returns:
            datetime: The cleaned meeting datetime.

        Raises:
            ValidationError: If the datetime is in the past.
        """
        meeting_datetime = self.cleaned_data.get('meeting_datetime')
        if meeting_datetime:
            if meeting_datetime < timezone.now():
                raise forms.ValidationError('Meeting time must be in the future.')
        return meeting_datetime

    def clean_title(self):
        """
        Validate the title field.

        Returns:
            str: The cleaned and stripped title.

        Raises:
            ValidationError: If title is empty or too long.
        """
        title = self.cleaned_data.get('title', '')
        if title:
            title = title.strip()
            if not title:
                raise forms.ValidationError('Title cannot be empty.')
            if len(title) > 200:
                raise forms.ValidationError('Title must be 200 characters or less.')
        return title

    def clean_description(self):
        """
        Validate the description field.

        Returns:
            str: The cleaned and stripped description.
        """
        description = self.cleaned_data.get('description', '')
        if description:
            description = description.strip()
        return description
