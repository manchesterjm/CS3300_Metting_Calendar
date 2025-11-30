"""
Authentication views for the calendar application.

This module contains views for user registration, login, logout,
and account management.

Views:
    - register_view: User registration with password validation
    - login_view: User authentication
    - logout_view: Session termination
    - account_view: User profile management

Security Features: Login required decorators, password validation, session management.
"""
import logging
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, IntegrityError, transaction
from django.shortcuts import render, redirect
from django.http import HttpResponseServerError
from django.utils.http import url_has_allowed_host_and_scheme
from .auth_forms import UserRegistrationForm, CustomAuthenticationForm, UserProfileForm

# Configure logger for authentication module
logger = logging.getLogger(__name__)


def register_view(request):
    """
    Handle user registration.

    Displays registration form on GET request and processes registration
    on POST request. Automatically logs in user after successful registration.

    Args:
        request: HttpRequest object.

    Returns:
        HttpResponse: Rendered registration template or redirect to calendar.
    """
    if request.user.is_authenticated:
        return redirect('calendar')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Use atomic transaction for database operations only
                with transaction.atomic():
                    user = form.save()
                    # Verify user was saved successfully
                    if not user.id:
                        raise ValueError('Failed to create user account - user ID is None')

            except IntegrityError as e:
                logger.error('Database integrity error during registration: %s', e)
                messages.error(request, 'Username or email already exists. Please try again.')
            except DatabaseError as e:
                logger.error('Database error during registration: %s', e)
                messages.error(request, 'An error occurred while creating your account. Please try again later.')
                return HttpResponseServerError('Internal server error')
            except ValueError as e:
                logger.error('User creation validation error: %s', e)
                messages.error(request, 'Account creation failed. Please try again.')
            else:
                # Success path - login after successful transaction
                # Session operations outside transaction block
                login(request, user)
                messages.success(
                    request,
                    f'Welcome {user.username}! Your account has been created successfully.'
                )
                logger.info('New user registered and logged in: %s', user.username)
                return redirect('calendar')
    else:
        form = UserRegistrationForm()

    return render(request, 'calendar_app/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.

    Displays login form on GET request and processes authentication on POST.
    Redirects to calendar page after successful login.

    Args:
        request: HttpRequest object.

    Returns:
        HttpResponse: Rendered login template or redirect to calendar.
    """
    if request.user.is_authenticated:
        return redirect('calendar')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # SECURITY: Validate redirect URL to prevent open redirect attacks
            # Only allow redirects to same domain to prevent phishing
            next_url = request.GET.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(next_url)
            # Default safe redirect if next URL is missing or unsafe
            return redirect('calendar')
        messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'calendar_app/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Handle user logout.

    Logs out the current user and redirects to login page.
    Requires user to be logged in.

    Args:
        request: HttpRequest object.

    Returns:
        HttpResponse: Redirect to login page.
    """
    username = request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {username}! You have been logged out.')
    return redirect('login')


@login_required
def account_view(request):
    """
    Handle user account management.

    Displays and processes user profile update form. Allows users to
    update their email, first name, and last name.

    Args:
        request: HttpRequest object.

    Returns:
        HttpResponse: Rendered account template.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Your account information has been updated.')
                logger.info('User %s updated their profile', request.user.username)
                return redirect('account')
            except DatabaseError as e:
                logger.error('Database error updating profile for %s: %s', request.user.username, e)
                messages.error(request, 'An error occurred while updating your profile. Please try again later.')
    else:
        form = UserProfileForm(instance=request.user)

    # Get user's unavailability count with error handling
    try:
        unavailability_count = request.user.unavailabilities.count()
    except DatabaseError as e:
        logger.error('Database error retrieving unavailability count for %s: %s', request.user.username, e)
        unavailability_count = 0
        messages.warning(request, 'Could not load some account statistics.')

    context = {
        'form': form,
        'unavailability_count': unavailability_count,
    }
    return render(request, 'calendar_app/account.html', context)
