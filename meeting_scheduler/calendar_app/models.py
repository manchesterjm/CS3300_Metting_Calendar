# calendar_app/models.py
# standard file, just updated it with what I needed for the date and time fields
from django.db import models

class Unavailability(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.date} from {self.start_time} to {self.end_time}"
