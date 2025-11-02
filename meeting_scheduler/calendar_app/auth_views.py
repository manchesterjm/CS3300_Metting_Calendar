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
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .auth_forms import UserRegistrationForm, CustomAuthenticationForm, UserProfileForm


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
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Welcome {user.username}! Your account has been created successfully.'
            )
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
            # Redirect to 'next' parameter if provided, otherwise to calendar
            next_url = request.GET.get('next', 'calendar')
            return redirect(next_url)
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
            form.save()
            messages.success(request, 'Your account information has been updated.')
            return redirect('account')
    else:
        form = UserProfileForm(instance=request.user)

    # Get user's unavailability count
    unavailability_count = request.user.unavailabilities.count()

    context = {
        'form': form,
        'unavailability_count': unavailability_count,
    }
    return render(request, 'calendar_app/account.html', context)
