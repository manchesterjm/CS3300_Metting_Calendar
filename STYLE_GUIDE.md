# Python/Django Style Guide

**Meeting Scheduler - Coding Standards**

**Version**: 2.0
**Last Updated**: January 11, 2025
**Project**: CS3300 Meeting Scheduler Application

This document defines the coding standards for all Python and Django code in this project. All team members must follow these guidelines to ensure consistency, maintainability, and code quality.

---

## Table of Contents

1. [General Principles](#general-principles)
2. [Python Style (PEP 8)](#python-style-pep-8)
3. [Django Conventions](#django-conventions)
4. [Naming Conventions](#naming-conventions)
5. [Code Organization](#code-organization)
6. [Functions and Methods](#functions-and-methods)
7. [Documentation](#documentation)
8. [Error Handling](#error-handling)
9. [Imports](#imports)
10. [Type Hints](#type-hints)
11. [Testing Standards](#testing-standards)
12. [Database and Models](#database-and-models)
13. [Templates and Frontend](#templates-and-frontend)
14. [Security Practices](#security-practices)
15. [Performance Considerations](#performance-considerations)
16. [Code Review Checklist](#code-review-checklist)

---

## General Principles

### Core Values
1. **Readability First**: Code is read more often than written
2. **Explicit is Better Than Implicit**: Clear over clever
3. **Consistency**: Follow existing patterns in the codebase
4. **DRY (Don't Repeat Yourself)**: Extract common functionality
5. **YAGNI (You Aren't Gonna Need It)**: Don't build for hypothetical futures
6. **Separation of Concerns**: Each component should have a single responsibility

### Code Quality Standards
- **Pylint Score**: Maintain ≥9.0/10 (current: 9.98/10)
- **Test Coverage**: Maintain ≥93% on critical modules (current: 93%+ on models, forms, views)
- **Overall Coverage**: Maintain ≥74% (current: 74%)
- **All Tests Must Pass**: No commits with failing tests
- **Mutation Score**: Maintain 100% (current: 8/8 killed)
- **No Warnings in Production**: Address all linter warnings before merging

---

## Python Style (PEP 8)

### Line Length
```python
# Maximum line length: 120 characters
# This is more permissive than PEP 8's 79, suitable for modern displays

# BAD: Line too long
def some_function():
    logger.info(f"This is a very long message that exceeds the maximum line length and should be broken into multiple lines for readability")

# GOOD: Line broken appropriately
def some_function():
    logger.info(
        "This is a very long message that has been broken into "
        "multiple lines for better readability"
    )
```

### Indentation
```python
# Use 4 spaces per indentation level (never tabs)

# GOOD
def calculate_total(items):
    total = 0
    for item in items:
        if item.is_valid:
            total += item.price
    return total
```

### Blank Lines
```python
# Two blank lines between top-level definitions
class FirstClass:
    pass


class SecondClass:
    pass


# One blank line between method definitions
class MyClass:
    def first_method(self):
        pass

    def second_method(self):
        pass


# Use blank lines sparingly inside functions to show logical sections
def complex_function():
    # Setup
    data = fetch_data()

    # Processing
    processed = transform(data)

    # Return
    return processed
```

### Whitespace
```python
# Whitespace in expressions and statements

# GOOD
x = 1
y = 2
long_variable = 3

# BAD
x             = 1
y             = 2
long_variable = 3

# GOOD
spam(ham[1], {eggs: 2})

# BAD
spam( ham[ 1 ], { eggs: 2 } )

# GOOD
if x == 4:
    print(x, y)
    x, y = y, x

# BAD
if x == 4 :
    print(x , y)
    x , y = y , x
```

---

## Django Conventions

### Project Structure
```
CS3300_project/
└── meeting_scheduler/           # Django project root
    ├── manage.py                # Django management script
    ├── db.sqlite3               # SQLite database
    ├── meeting_scheduler/       # Project settings
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── calendar_app/            # Main Django app
        ├── migrations/
        ├── templates/
        │   └── calendar_app/
        ├── admin.py
        ├── apps.py
        ├── forms.py
        ├── models.py            # Unavailability, Group models
        ├── views.py             # Personal calendar views
        ├── group_views.py       # Group calendar views
        ├── auth_views.py        # Authentication views
        ├── tests.py             # Unit tests (93 tests)
        ├── test_fuzz.py         # Fuzz tests (16 tests)
        ├── test_debug_crud.py   # Debug/integration tests
        └── urls.py
```

### Model Conventions
```python
# Models should be singular nouns
class User(models.Model):  # GOOD
class Users(models.Model):  # BAD

# Field ordering: database fields, then Meta, then methods
class Unavailability(models.Model):
    # Database fields (in logical order)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=200, blank=True)

    # Metadata
    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Unavailability'
        verbose_name_plural = 'Unavailabilities'

    # String representation
    def __str__(self):
        return f"{self.user.username} - {self.date} {self.start_time}-{self.end_time}"

    # Custom methods
    def duration_hours(self):
        """Calculate duration in hours."""
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        return (end_dt - start_dt).total_seconds() / 3600
```

### View Conventions
```python
# Use function-based views for simple logic
def home_view(request):
    """Display the home/landing page."""
    return render(request, 'calendar_app/home.html')

# Function-based views with complex logic
@login_required
def calendar_view(request):
    """Display and manage user's personal calendar."""
    if request.method == 'POST':
        if 'submit_unavailability' in request.POST:
            # Handle unavailability form
            pass
        elif 'show_free_times' in request.POST:
            # Calculate free time slots
            pass

    return render(request, 'calendar_app/calendar.html', context)

# Use class-based views for CRUD operations when appropriate
from django.views.generic import ListView, DetailView

class GroupListView(LoginRequiredMixin, ListView):
    """Display list of user's groups."""
    model = Group
    template_name = 'calendar_app/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user)
```

### URL Patterns
```python
# Use descriptive URL names for reverse lookups
urlpatterns = [
    path('', views.home_view, name='home'),              # GOOD
    path('', views.home_view, name='view1'),             # BAD

    # Use path() over re_path() when possible
    path('groups/<int:group_id>/', views.group_detail_view, name='group_detail'),  # GOOD
    re_path(r'^groups/(?P<group_id>\d+)/$', views.group_detail_view),              # BAD

    # Group related URLs
    path('calendar/', views.calendar_view, name='calendar'),
    path('groups/', views.group_list_view, name='group_list'),
    path('groups/create/', views.group_create_view, name='group_create'),
    path('groups/<int:group_id>/calendar/', views.group_calendar_view, name='group_calendar'),
]
```

### Admin Customization

```python
# IMPORTANT: Admin User Customization Pattern
# This project uses unregister/re-register pattern for User admin
# See calendar_app/admin.py for full documentation

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Unregister default User admin (only do this in ONE app!)
admin.site.unregister(User)

class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with password generation."""
    change_password_template = 'admin/auth/user/change_password.html'

# Re-register with custom admin
admin.site.register(User, CustomUserAdmin)
```

**⚠️ Warning: Admin Customization Risks**
- Only ONE app should customize User admin (currently: `calendar_app/admin.py`)
- Multiple apps customizing the same model causes `AlreadyRegistered` exception
- App loading order in `INSTALLED_APPS` matters (customizing app should load last)
- For larger projects, consider using a custom User model instead

**Alternatives:**
1. **Custom User Model** (recommended for production):
   ```python
   # In models.py
   class CustomUser(AbstractUser):
       pass

   # In settings.py
   AUTH_USER_MODEL = 'calendar_app.CustomUser'
   ```
2. **Centralized admin.py**: Put all admin customizations in one location
3. **Admin Proxy Models**: Use proxy models for read-only admin views

**Current Status**: `calendar_app` is the ONLY app customizing User admin (✓ Safe)

---

## Naming Conventions

### General Rules
```python
# Variables and functions: lowercase_with_underscores
user_count = 10
def get_user_profile():
    pass

# Classes: CapitalizedWords (PascalCase)
class UserProfile:
    pass

# Constants: UPPERCASE_WITH_UNDERSCORES
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_TIMEOUT = 300

# "Private" (internal): single leading underscore
def _internal_helper():
    pass

_internal_variable = "hidden"

# Name mangling (rarely used): double leading underscore
class MyClass:
    def __private_method(self):
        pass
```

### Django-Specific Naming
```python
# Model fields: descriptive, lowercase_with_underscores
class Unavailability:
    created_at = models.DateTimeField(auto_now_add=True)  # GOOD
    created = models.DateTimeField(auto_now_add=True)      # OK but less clear
    dt = models.DateTimeField(auto_now_add=True)           # BAD

# Related names: plural for reverse relations
class GroupMembership(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='memberships'  # group.memberships.all()
    )

# View function names: verb_noun or noun_verb pattern
def list_groups(request):          # GOOD
def group_list(request):           # GOOD
def groups(request):               # Less clear
def view1(request):                # BAD

# URL names: noun_verb or app_noun_verb
name='group_list'                  # GOOD
name='calendar_view'               # GOOD
name='groups'                      # Less clear
```

### Boolean Variables
```python
# Use is_, has_, can_, should_ prefixes for booleans
is_active = True
has_permission = False
can_edit = True
should_retry = False

# BAD
active = True      # Ambiguous
permission = False # What does False mean?
```

---

## Code Organization

### File Organization
```python
"""
Module docstring explaining the purpose of this file.

This module handles user authentication and session management.
"""

# Standard library imports
import logging
import time
from datetime import datetime, timedelta

# Third-party imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Local application imports
from .models import Unavailability, Group
from .forms import UnavailabilityForm, DeleteSelectedForm

# Constants
MAX_LOGIN_ATTEMPTS = 3
LOGIN_TIMEOUT = 300

# Module-level variables (if necessary)
logger = logging.getLogger(__name__)

# Functions and classes (in logical order)
```

### Import Ordering
```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party packages
import django
from django.db import models
from hypothesis import given

# 3. Local application/library specific
from .models import User
from .utils import helper_function

# Within each group, imports should be alphabetical
```

---

## Functions and Methods

### Single Return Statement Principle
```python
# GOOD: Single return point (when practical)
def calculate_discount(price, user):
    """Calculate discount for user purchase."""
    # Guard clauses for validation (early returns OK)
    if price <= 0:
        return 0
    if not user.is_authenticated:
        return 0

    # Main logic with single return
    discount = 0
    if user.is_premium:
        discount = price * 0.20
    elif user.has_membership:
        discount = price * 0.10

    return discount

# ACCEPTABLE: Multiple returns for validation/error cases
def process_payment(amount, user):
    """Process payment for user."""
    # Early returns for error conditions
    if amount <= 0:
        return None, "Invalid amount"

    if not user.has_payment_method:
        return None, "No payment method"

    # Main logic
    result = charge_payment(amount, user)
    return result, "Success"
```

### Function Length
```python
# Keep functions focused and concise (generally <50 lines)
# If longer, consider breaking into smaller functions

# BAD: Too long, does too many things
def process_order(order):
    # 100+ lines of mixed validation, processing, email, logging...
    pass

# GOOD: Broken into logical pieces
def process_order(order):
    """Process customer order."""
    if not _validate_order(order):
        return False

    _update_inventory(order)
    _charge_customer(order)
    _send_confirmation_email(order)
    _log_order_completion(order)

    return True

def _validate_order(order):
    """Validate order has required fields."""
    return order.items and order.customer

def _update_inventory(order):
    """Update inventory for order items."""
    for item in order.items:
        item.product.decrease_stock(item.quantity)
```

### Function Arguments
```python
# Limit function arguments (≤5 is ideal, ≤7 maximum)

# BAD: Too many arguments
def create_user(username, email, password, first_name, last_name,
                phone, address, city, state, zip_code):
    pass

# GOOD: Group related data into objects/dicts
def create_user(username, email, password, profile_data):
    """
    Create new user account.

    Args:
        username: Unique username
        email: User email address
        password: Raw password (will be hashed)
        profile_data: Dict with keys: first_name, last_name, phone, address
    """
    pass

# Or use a dataclass/NamedTuple for structured data
from dataclasses import dataclass

@dataclass
class UserProfile:
    first_name: str
    last_name: str
    phone: str
    address: str

def create_user(username, email, password, profile: UserProfile):
    pass
```

### Default Arguments
```python
# Never use mutable default arguments

# BAD
def add_item(item, items=[]):
    items.append(item)
    return items

# GOOD
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## Documentation

### Docstrings
```python
# All modules, classes, and public functions must have docstrings

# Module docstring
"""
User authentication and authorization module.

This module provides functionality for user login, logout, password reset,
and permission checking.
"""

# Function docstring (Google style)
def calculate_free_slots(date, unavailabilities, start_hour=8, end_hour=20):
    """
    Calculate free 30-minute time slots for a given date.

    Args:
        date: Date to check for free slots
        unavailabilities: QuerySet of Unavailability objects for the date
        start_hour: Starting hour for schedule (default: 8 AM)
        end_hour: Ending hour for schedule (default: 8 PM)

    Returns:
        List[str]: List of free time slots in "HH:MM-HH:MM" format

    Raises:
        ValueError: If start_hour >= end_hour

    Example:
        >>> slots = calculate_free_slots(today, user_unavail)
        >>> print(slots)
        ['08:00-08:30', '08:30-09:00', '10:00-10:30', ...]
    """
    if start_hour >= end_hour:
        raise ValueError("Start hour must be before end hour")

    # Implementation...
    return free_slots

# Class docstring
class Unavailability(models.Model):
    """
    User unavailability record for calendar scheduling.

    Stores time periods when a user is not available for meetings.
    Used to calculate free time slots and group availability.

    Attributes:
        user: ForeignKey to Django User model
        date: Date of unavailability
        start_time: Start time of unavailability period
        end_time: End time of unavailability period
        description: Optional description (e.g., "Meeting", "Lunch")
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    # ...
```

### Code Comments
```python
# Use comments to explain WHY, not WHAT

# BAD: Comment states the obvious
# Increment counter by 1
counter += 1

# GOOD: Comment explains reasoning
# Add 1 to account for zero-indexing in display
counter += 1

# BAD: Redundant comment
# Get user by ID
user = User.objects.get(id=user_id)

# GOOD: Explains business logic
# Group calendar only shows times when ALL members are available
if all_members_free(time_slot, group):
    available_slots.append(time_slot)

# Use TODO comments for future improvements
# TODO(username): Add pagination when entry count exceeds 100
entries = Unavailability.objects.filter(user=user).all()

# Use FIXME for known issues
# FIXME(username): Time zone handling needed for multi-region groups
update_schedule()
```

### Django Model Documentation
```python
class Group(models.Model):
    """
    Scheduling group model.

    Represents a group of users who want to coordinate schedules
    and find common free times for meetings.
    """
    name = models.CharField(
        max_length=100,
        help_text="Group name (shown in group list)"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_groups',
        help_text="User who created this group"
    )
    members = models.ManyToManyField(
        User,
        related_name='groups',
        help_text="All group members including owner"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.name

    def get_common_free_times(self, date):
        """Calculate times when all group members are available."""
        # Implementation...
        pass
```

---

## Error Handling

### Exceptions
```python
# Use specific exceptions, not bare except

# BAD
try:
    user = User.objects.get(id=user_id)
except:
    return None

# GOOD
try:
    user = User.objects.get(id=user_id)
except User.DoesNotExist:
    logger.warning("User not found: %s", user_id)
    return None

# Catch multiple specific exceptions
try:
    result = process_payment(amount)
except (PaymentError, NetworkError) as e:
    logger.error("Payment failed: %s", str(e))
    return False

# Use broad exceptions only when necessary, with justification
try:
    plugin.execute()
except Exception as e:  # pylint: disable=broad-exception-caught
    # Catch all to prevent plugin failures from crashing app
    logger.error("Plugin execution failed: %s", type(e).__name__)
```

### Error Messages
```python
# Error messages should be clear and actionable

# BAD
raise ValueError("Invalid input")

# GOOD
raise ValueError(
    f"Invalid time range: start_time ({start_time}) must be before "
    f"end_time ({end_time})"
)

# For user-facing errors, don't expose internal details
# BAD (security issue)
return JsonResponse({
    'error': f'Database error: {str(e)}'
})

# GOOD
logger.error("Database error processing request: %s", str(e))
return JsonResponse({
    'error': 'An error occurred. Please try again later.'
})
```

### Validation
```python
# Validate early, fail fast

def create_unavailability(user, date, start_time, end_time):
    """Create unavailability entry for user."""
    # Validation at the top
    if not user.is_authenticated:
        raise ValueError("User must be authenticated")
    if start_time >= end_time:
        raise ValueError("Start time must be before end time")
    if date < datetime.date.today():
        raise ValueError("Cannot create entry for past dates")

    # Main logic after validation
    unavail = Unavailability.objects.create(
        user=user,
        date=date,
        start_time=start_time,
        end_time=end_time
    )

    return unavail
```

---

## Imports

### Order and Organization
```python
# Group imports in this order:
# 1. Standard library
# 2. Third-party packages
# 3. Local application

# Within each group, alphabetize by module name

# GOOD
import logging
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect

from .forms import UnavailabilityForm
from .models import Unavailability, Group

# BAD - mixed ordering
from .models import Unavailability
import os
from django.contrib.auth import authenticate
import logging
```

### Import Styles
```python
# Prefer importing modules, not names

# GOOD
from django.contrib import auth
user = auth.authenticate(username=username, password=password)

# ACCEPTABLE
from django.contrib.auth import authenticate
user = authenticate(username=username, password=password)

# Avoid wildcard imports
# BAD
from django.contrib.auth import *

# Avoid relative imports that go up multiple levels
# BAD
from ....utils import helper

# GOOD
from calendar_app.utils import helper
```

---

## Type Hints

### Usage
```python
# Use type hints for function signatures (Python 3.9+)

from typing import List, Dict, Optional, Union, QuerySet
from datetime import date, time

def calculate_free_slots(
    target_date: date,
    unavailabilities: QuerySet,
    start_hour: int = 8,
    end_hour: int = 20
) -> List[str]:
    """Calculate free 30-minute time slots."""
    pass

# Use Optional for values that can be None
def get_group(group_id: int) -> Optional[Group]:
    """Retrieve group by ID, returns None if not found."""
    try:
        return Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return None

# Django model return types
def get_user_unavailabilities(user: User) -> QuerySet:
    """Get all unavailability entries for user."""
    return Unavailability.objects.filter(user=user).order_by('-date')
```

---

## Testing Standards

See also: **CLAUDE.md** and **TESTING_WORKFLOW.md** for comprehensive testing guidance.

### Test Organization
```python
# Organize tests by feature/model
class UnavailabilityModelTests(TestCase):
    """Tests for Unavailability model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_unavailability_creation(self):
        """Test unavailability entry is created with correct attributes."""
        unavail = Unavailability.objects.create(
            user=self.user,
            date=datetime.date.today(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )
        self.assertEqual(unavail.user, self.user)
        self.assertEqual(unavail.start_time, datetime.time(9, 0))

    def test_unavailability_str_representation(self):
        """Test string representation of unavailability."""
        unavail = Unavailability.objects.create(
            user=self.user,
            date=datetime.date.today(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )
        expected = f"testuser - {datetime.date.today()} 09:00:00-10:00:00"
        self.assertEqual(str(unavail), expected)
```

### Test Naming
```python
# Test names should describe what they test

# GOOD
def test_login_with_invalid_password_fails(self):
def test_user_can_delete_own_unavailability(self):
def test_group_calendar_shows_common_free_times(self):

# BAD
def test_login(self):
def test_user(self):
def test_1(self):
```

### Test Independence
```python
# Each test must be completely independent

# BAD
class BadTestClass(TestCase):
    def test_create_unavailability(self):
        self.unavail = Unavailability.objects.create(...)

    def test_update_unavailability(self):
        # Depends on test_create_unavailability running first!
        self.unavail.description = 'Updated'
        self.unavail.save()

# GOOD
class GoodTestClass(TestCase):
    def setUp(self):
        """Create fresh test data for each test."""
        self.user = User.objects.create_user(username='test')
        self.unavail = Unavailability.objects.create(
            user=self.user,
            date=datetime.date.today(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )

    def test_create_unavailability(self):
        new_unavail = Unavailability.objects.create(...)
        self.assertIsNotNone(new_unavail.id)

    def test_update_unavailability(self):
        self.unavail.description = 'Updated'
        self.unavail.save()
        self.unavail.refresh_from_db()
        self.assertEqual(self.unavail.description, 'Updated')
```

### Mocking
```python
# Mock external dependencies to prevent flaky tests

from unittest.mock import patch, MagicMock

class EmailTestCase(TestCase):
    @patch('calendar_app.auth_views.send_mail')
    def test_password_reset_sends_email(self, mock_send_mail):
        """Test password reset sends email to user."""
        mock_send_mail.return_value = 1

        response = self.client.post('/password-reset/', {
            'email': 'test@example.com'
        })

        self.assertEqual(response.status_code, 200)
        mock_send_mail.assert_called_once()
```

---

## Database and Models

### Query Optimization
```python
# Use select_related for foreign keys (one-to-one, many-to-one)
unavailabilities = Unavailability.objects.select_related('user').all()

# Use prefetch_related for reverse foreign keys (one-to-many, many-to-many)
groups = Group.objects.prefetch_related('members').all()

# Combine for complex queries
groups = Group.objects.select_related(
    'created_by'
).prefetch_related(
    'members',
    'members__unavailability_set'
).all()

# Use only() or defer() to limit fields
users = User.objects.only('username', 'email').all()
```

### Model Methods
```python
# Put business logic in model methods, not views

# GOOD
class Group(models.Model):
    def get_common_free_times(self, date):
        """Calculate common free times for all group members."""
        # Get all members' unavailabilities
        all_unavail = Unavailability.objects.filter(
            user__in=self.members.all(),
            date=date
        )
        # Calculate common free slots
        return calculate_free_slots(date, all_unavail)

# In view
group = Group.objects.get(id=group_id)
free_times = group.get_common_free_times(target_date)

# BAD - logic in view
group = Group.objects.get(id=group_id)
members = group.members.all()
all_unavail = Unavailability.objects.filter(user__in=members, date=date)
free_times = calculate_free_slots(date, all_unavail)
```

---

## Templates and Frontend

### Template Organization
```python
# Use template inheritance
# base.html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Meeting Scheduler{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

# calendar.html
{% extends 'calendar_app/base.html' %}

{% block title %}My Calendar - Meeting Scheduler{% endblock %}

{% block content %}
    <h1>My Calendar</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Submit</button>
    </form>
{% endblock %}
```

### Template Logic
```python
# Keep logic in views, not templates

# BAD - complex logic in template
{% for unavail in unavailabilities %}
    {% if unavail.date >= today and unavail.user == request.user and unavail.start_time >= now %}
        ...
    {% endif %}
{% endfor %}

# GOOD - filter in view
def calendar_view(request):
    unavailabilities = Unavailability.objects.filter(
        user=request.user,
        date__gte=datetime.date.today()
    ).order_by('date', 'start_time')
    return render(request, 'calendar_app/calendar.html',
                  {'unavailabilities': unavailabilities})
```

---

## Security Practices

See **SECURITY_GUIDE.md** for comprehensive security guidelines.

### Quick Reference
- Never commit secrets or API keys
- Use environment variables for sensitive data (SECRET_KEY, email credentials)
- Validate all user input (dates, times, form data)
- Use Django's built-in protections (CSRF, XSS, SQL injection)
- Use HTTPS in production
- Implement rate limiting for authentication endpoints
- Log security events with IP addresses
- Use generic error messages (prevent user enumeration)

---

## Performance Considerations

### Database Queries
```python
# Avoid N+1 queries
# BAD
groups = Group.objects.all()
for group in groups:
    print(group.created_by.username)  # Separate query for each user!

# GOOD
groups = Group.objects.select_related('created_by').all()
for group in groups:
    print(group.created_by.username)  # No extra queries
```

### Caching
```python
# Use Django's cache framework for expensive operations
from django.core.cache import cache

def get_user_free_times(user, date):
    """Get user free times with 5-minute cache."""
    cache_key = f'free_times_{user.id}_{date}'
    free_times = cache.get(cache_key)

    if free_times is None:
        unavail = Unavailability.objects.filter(user=user, date=date)
        free_times = calculate_free_slots(date, unavail)
        cache.set(cache_key, free_times, 300)  # 5 minutes

    return free_times
```

---

## Code Review Checklist

### Before Submitting PR
- [ ] All tests pass locally (141 tests)
- [ ] Pylint score ≥9.0 (no disabled errors)
- [ ] Test coverage maintained or improved (≥93% on critical modules)
- [ ] Mutation score maintained at 100%
- [ ] Security scans passed (Bandit, pip-audit)
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Docstrings added for new functions/classes
- [ ] CLAUDE.md updated if architecture changes
- [ ] Type hints added for function signatures
- [ ] Security considerations addressed
- [ ] Performance implications considered

### Reviewing Code
- [ ] Code follows this style guide
- [ ] Tests are independent and not flaky
- [ ] Error handling is appropriate
- [ ] No sensitive data in code or logs
- [ ] Database queries are optimized
- [ ] User input is validated
- [ ] Documentation is clear and complete
- [ ] Code is maintainable and readable

---

## Pylint Configuration and Disabled Warnings

This project uses Pylint for code quality enforcement with a target score of ≥9.0/10 (currently 9.98/10). Some Pylint warnings are disabled for valid architectural and framework-specific reasons. This section documents each disabled warning and the justification.

### Command-Line Disabled Warnings

These warnings are disabled globally when running Pylint (see CLAUDE.md for test commands):

```bash
pylint calendar_app/*.py --disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101 --max-line-length=120
```

**C0114, C0115, C0116: Missing docstrings**
- **Reason**: Code comments provide sufficient documentation inline
- **Justification**: This is a small educational project where inline comments explain logic. Docstrings are used for complex functions and classes, but not enforced universally.
- **Alternative**: Critical functions and classes DO have docstrings (see Documentation section)

**R0903: Too few public methods**
- **Reason**: Django models and forms often have minimal methods by design
- **Justification**: Django's ModelForm, DeleteForm, and similar classes are primarily data containers with validation logic in clean() methods
- **Example**: `DeleteSelectedForm` only has form fields, no custom methods needed

**R0914: Too many locals**
- **Reason**: Single-view architecture with multiple POST actions
- **Justification**: The `calendar_view` handles multiple form submissions (add, delete, show_free_times, show_last_five) in one view function per Django best practices
- **Alternative**: Could split into multiple views, but current architecture is clearer for this project's scope

**R0912: Too many branches**
- **Reason**: Single-view architecture handles multiple POST button actions
- **Justification**: Views use `if 'button_name' in request.POST` pattern to route to different actions
- **Alternative**: The complexity is inherent to the design pattern, not poor code quality

**R0915: Too many statements**
- **Reason**: Views handle form processing, validation, and database operations
- **Justification**: Breaking views into smaller functions would reduce clarity for this project's scale
- **Alternative**: Accepted as reasonable for educational Django project

**E1101: Django ORM 'objects' member**
- **Reason**: Pylint doesn't recognize Django's ORM `objects` manager
- **Justification**: `User.objects`, `Unavailability.objects` are dynamically added by Django
- **Alternative**: Use `django-pylint` plugin (not currently configured)

### In-Code Disabled Warnings

These warnings are disabled inline for specific code sections with `# pylint: disable=warning-name`:

**duplicate-code (group_views.py:7)**
- **Reason**: Intentional similarity between personal and group calendar views
- **Justification**: Group calendar logic is similar to personal calendar but operates on aggregated data
- **Files**: `views.py` and `group_views.py` share validation/calculation patterns
- **Alternative**: Shared logic extracted to `utils.py` where appropriate

**too-many-ancestors (auth_forms.py:13, forms.py:55, forms.py:249)**
- **Reason**: Django form inheritance chain (ModelForm → BaseDescriptionForm → our forms)
- **Justification**: This is the standard Django pattern for forms with custom validation
- **Files**:
  - `UserRegistrationForm` inherits from `UserCreationForm` (Django)
  - `UnavailabilityForm` and `GroupUnavailabilityForm` inherit from `BaseDescriptionForm` + `ModelForm`
- **Alternative**: None - this is idiomatic Django

**protected-access (email_backend.py:51, email_backend.py:61)**
- **Reason**: Accessing `_lock` attribute for SSL context workaround
- **Justification**: Development-only SSL bypass for Windows certificate issues (see email_backend.py docstring)
- **Security**: Runtime check prevents production use:
  ```python
  if settings.DEBUG and platform.system() == 'Windows':
      # SSL bypass only in Windows development
  ```
- **Alternative**: Use console email backend in development (current default)

**unused-argument (auth_views.py:215)**
- **Reason**: Django view signature requires `request` even if not used
- **Justification**: POST endpoint `generate_password_api` doesn't need request data, only CSRF token
- **Files**: `auth_views.py:generate_password_api(request)`
- **Alternative**: None - Django views must accept `request`

**too-many-lines (tests.py:29)**
- **Reason**: Comprehensive test suite in single file (currently ~1350 lines)
- **Justification**: Current structure groups all tests by feature for easy navigation
- **Status**: **Planned for refactoring** (see AI Code Review Fix #14)
- **Alternative**: Split into `tests/test_models.py`, `tests/test_forms.py`, `tests/test_views.py`, etc.

**too-many-arguments, too-many-positional-arguments (test_fuzz.py:11)**
- **Reason**: Hypothesis fuzz testing generates many parameter combinations
- **Justification**: Fuzz tests intentionally test with many input variations
- **Files**: `test_fuzz.py` - property-based tests with `@given` decorator
- **Alternative**: None - this is how Hypothesis framework works

**broad-exception-caught (test_fuzz.py:11)**
- **Reason**: Fuzz tests need to catch all exceptions to verify robustness
- **Justification**: Testing that code doesn't crash with unexpected inputs requires catching broad exceptions
- **Alternative**: None - fuzz testing specifically targets unexpected failures

### Guidelines for Adding New Disables

When adding a new Pylint disable:

1. **Consider alternatives first** - Is there a better way to structure the code?
2. **Document inline** - Add comment explaining why disable is needed
3. **Use specific scope** - Disable at the smallest scope (line > function > file)
4. **Update this guide** - Add entry to this section with justification
5. **Review regularly** - Revisit disables when refactoring

**Example:**
```python
def my_function(request):  # pylint: disable=unused-argument
    # Django view signature requires 'request' parameter
    # even though this simple view doesn't use it
    return JsonResponse({'status': 'ok'})
```

**Never disable these warnings:**
- Security-related warnings (SQL injection, XSS, etc.)
- Logic errors (undefined-variable, no-member, etc.)
- Import errors (import-error, no-name-in-module, etc.)

If you encounter these, fix the code rather than disabling the warning.

---

## Enforcement

### Automated Checks
- **Pylint**: Runs on all PRs, must score ≥9.0
- **Tests**: All 141 tests must pass before merge
- **Coverage**: Must maintain ≥93% on critical modules (models.py, forms.py, views.py)
- **Mutation Score**: Must maintain 100%
- **Security**: Bandit and pip-audit must pass

### Manual Review
- All PRs require review by at least one team member
- Reviewers should reference this guide when providing feedback
- Style violations should be fixed before merge

---

## Exceptions and Special Cases

### When to Deviate
- **Legacy Code**: Gradual refactoring is acceptable
- **Third-Party Integration**: Match external API conventions when necessary
- **Performance Critical**: Document why standard approach wasn't used
- **Proof of Concepts**: Clearly mark as experimental

### How to Request Exception
1. Document reason in code comments
2. Note in PR description
3. Get team consensus if significant deviation

---

## Resources

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Django Coding Style](https://docs.djangoproject.com/en/stable/internals/contributing/writing-code/coding-style/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [CLAUDE.md](./CLAUDE.md) - Project-specific development guide
- [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) - Security best practices
- [TESTING_WORKFLOW.md](./meeting_scheduler/TESTING_WORKFLOW.md) - Testing requirements

---

## Changelog

### Version 2.1 (November 3, 2025)
- Added comprehensive "Pylint Configuration and Disabled Warnings" section
- Documented all command-line and in-code Pylint disables with justifications
- Added guidelines for adding new Pylint disables
- Added "Admin Customization" section documenting User admin unregister/re-register pattern
- Enhanced admin.py module docstring with comprehensive pattern documentation
- Addressed AI Code Review Fixes #10 and #12

### Version 2.0 (January 11, 2025)
- Updated for Meeting Scheduler project (CS3300)
- Updated code quality standards (9.98/10 Pylint, 93%+ coverage on critical modules)
- Updated project structure and examples to match calendar_app
- Updated test statistics (141 tests, 100% mutation score)
- Integrated with current security scanning tools (Bandit, pip-audit, Semgrep)

### Version 1.0 (October 29, 2024)
- Initial style guide creation
- Established baseline standards
- Integrated with pylint configuration
- Added single return statement guideline
- Comprehensive testing standards

---

**Questions or Suggestions?**
Open an issue or discuss in team meetings. This guide is a living document and will evolve with the project.
