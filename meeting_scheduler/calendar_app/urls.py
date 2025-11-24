"""
URL configuration for the calendar application.

This module defines URL patterns for routing requests to the calendar
application views, including authentication, groups, and meeting proposals.

Version: 3.0 (Join Codes + Recurring + Meeting Proposals)
Last Updated: 2025-11-24
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home_view, calendar_view
from .auth_views import (
    login_view, logout_view, register_view, account_view,
    change_password_view, generate_password_api
)
from .group_views import (
    group_list_view,
    group_create_view,
    group_detail_view,
    group_calendar_view,
    group_add_member_view,
    group_remove_member_view,
    group_delete_view,
    join_group_view,
    generate_join_code_view,
    toggle_join_code_view
)
from .proposal_views import (
    create_proposal_view,
    proposal_list_view,
    respond_to_proposal_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('personal-calendar/', calendar_view, name='calendar'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('account/', account_view, name='account'),
    path('account/change-password/', change_password_view, name='change_password'),

    # API endpoints
    path('api/generate-password/', generate_password_api, name='generate_password_api'),

    # Group URLs
    path('groups/', group_list_view, name='group_list'),
    path('groups/create/', group_create_view, name='group_create'),
    path('groups/join/', join_group_view, name='join_group'),
    path('groups/<int:group_id>/', group_detail_view, name='group_detail'),
    path('groups/<int:group_id>/calendar/', group_calendar_view, name='group_calendar'),
    path('groups/<int:group_id>/add-member/', group_add_member_view, name='group_add_member'),
    path('groups/<int:group_id>/remove-member/<int:user_id>/',
         group_remove_member_view, name='group_remove_member'),
    path('groups/<int:group_id>/delete/', group_delete_view, name='group_delete'),
    path('groups/<int:group_id>/generate-join-code/', generate_join_code_view, name='generate_join_code'),
    path('groups/<int:group_id>/toggle-join-code/', toggle_join_code_view, name='toggle_join_code'),

    # Meeting Proposal URLs
    path('groups/<int:group_id>/proposals/', proposal_list_view, name='proposal_list'),
    path('groups/<int:group_id>/proposals/create/', create_proposal_view, name='create_proposal'),
    path('proposals/<int:proposal_id>/respond/<str:response_type>/',
         respond_to_proposal_view, name='respond_to_proposal'),

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
