"""
URL configuration for the calendar application.

This module defines URL patterns for routing requests to the calendar
application views. Currently maps the root path to the main calendar view.
"""
from django.urls import path
from .views import calendar_view

urlpatterns = [
    path('', calendar_view, name='calendar'),
]
