"""
Django application configuration for the calendar app.

Defines application settings and metadata for the Meeting Scheduler.
"""
from django.apps import AppConfig


class CalendarAppConfig(AppConfig):
    """Configuration class for the calendar application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendar_app'
    verbose_name = 'Meeting Scheduler Calendar'
