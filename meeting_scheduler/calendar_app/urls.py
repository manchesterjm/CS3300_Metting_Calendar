"""
URL configuration for the calendar application.

This module defines URL patterns for routing requests to the calendar
application views, including authentication and password reset endpoints.

Version: 2.0 (Group Calendar Support)
Last Updated: 2025-01-11
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import calendar_view
from .auth_views import login_view, logout_view, register_view, account_view
from .group_views import (
    group_list_view,
    group_create_view,
    group_detail_view,
    group_calendar_view,
    group_add_member_view,
    group_remove_member_view,
    group_delete_view
)

urlpatterns = [
    path('', calendar_view, name='calendar'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('account/', account_view, name='account'),

    # Group URLs
    path('groups/', group_list_view, name='group_list'),
    path('groups/create/', group_create_view, name='group_create'),
    path('groups/<int:group_id>/', group_detail_view, name='group_detail'),
    path('groups/<int:group_id>/calendar/', group_calendar_view, name='group_calendar'),
    path('groups/<int:group_id>/add-member/', group_add_member_view, name='group_add_member'),
    path('groups/<int:group_id>/remove-member/<int:user_id>/',
         group_remove_member_view, name='group_remove_member'),
    path('groups/<int:group_id>/delete/', group_delete_view, name='group_delete'),

    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='calendar_app/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='calendar_app/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='calendar_app/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='calendar_app/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
