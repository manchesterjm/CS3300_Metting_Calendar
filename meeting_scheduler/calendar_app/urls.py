# this is basically the default file that was generated when I installed django
# the only change was to set the path to the calendar_view from views.py

from django.urls import path
from .views import calendar_view

urlpatterns = [
    path('', calendar_view, name='calendar'),
]
