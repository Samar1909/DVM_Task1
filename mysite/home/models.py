from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
day_dict = {
    "MON" : 'Monday',
    "TUE" : 'Tuesday',
    "WED" : 'Wednesday',
    "THU" : 'Thursday',
    "FRI" : 'Friday',
    "SAT" : 'Saturday',
    "SUN" : 'Sunday'
}

class day(models.Model):
    day_code = models.CharField(max_length=3, choices=day_dict, unique=True)

    def __str__(self):
        return self.day_code


class bus(models.Model):
    bus_number = models.IntegerField(default = 10000, blank=False, null=False, validators=[MaxValueValidator(99999), MinValueValidator(10000)])
    name = models.CharField(default = 'bus_name', blank=False, null=False, max_length=50)
    city1 = models.CharField(max_length = 30)
    city2 = models.CharField(max_length = 30)
    seats_total = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    seats_available = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    days = models.ManyToManyField(day)
    time = models.TimeField(default = timezone.now, blank=False, null=False)
    duration = models.IntegerField(default = 0, null=False, blank=False, validators=[MaxValueValidator(24), MinValueValidator(1)])
        
    def __str__(self):
        return self.name

    def seats(self):
        self.seats_available = self.seats_total

    def save(self, *args, **kwargs):
        self.seats()
        super().save(*args, **kwargs)

class booking(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    bus  = models.ForeignKey(bus, on_delete = models.CASCADE)
    is_booked = models.BooleanField(default = False)

class account(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10000)])
