from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta
import logging

day_List = [('Mon', 'Monday'),
            ('Tue', 'Tuesday'),
            ('Wed', 'Wednesday'),
            ('Thu','Thursday'),
            ('Fri', 'Friday'),
            ('Sat', 'Saturday'),
            ('Sun', 'Sunday')]

day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Thu': 5, 'Sat': 6, 'Sun': 7}

time_validator = RegexValidator(r'^([01]\d|2[0-3])([0-5]\d)$', 'Enter a valid time in 24 hour format') 

# Create your models here.

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField

class bus(models.Model):  
    bus_number = models.IntegerField(
        validators=[MaxValueValidator(99999), MinValueValidator(10000)]  
    )
    name = models.CharField(max_length=50)  
    city1 = models.CharField(max_length=30)
    city2 = models.CharField(max_length=30)
    seats_total = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)],
        null=False
    )
    seats_available = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)],
        null=False
    )
    operating_days = ArrayField(
        models.CharField(max_length=10, choices=day_List),
        default=list,
        blank=False,
        null=False
    )
    time_start = models.CharField(
        max_length=4,
        validators=[time_validator],
        null=False
    )
    time_end = models.CharField(
        max_length=4,
        validators=[time_validator],
        null=False
    )
    fare = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.bus_number})"

    def initialize_seats(self):
        self.seats_available = self.seats_total

    def seat_validator(self):
        if self.seats_available is None or self.seats_total is None:
            raise ValueError("Seats available and total seats cannot be None")
            
        if self.seats_available > self.seats_total:
            raise ValueError("Number of available seats can't exceed total seats")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.initialize_seats()
        self.seat_validator()  
        super().save(*args, **kwargs)    
        

class ticket(models.Model):
    num = models.PositiveIntegerField(validators = [MinValueValidator(1)])
    users = models.ManyToManyField(User)
    bus  = models.ForeignKey(bus, on_delete = models.CASCADE)
    dateOfBooking = models.DateField(default=timezone.now)
    price = models.PositiveIntegerField(validators=[MaxValueValidator(10000)])
    city1 = models.CharField(max_length=50)
    city2 = models.CharField(max_length=50)

class passDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(ticket, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)

class wallet(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10000)], default=0)

    def __str__(self):
        return str(self.user)
    
class schedule(models.Model):
    bus = models.OneToOneField(bus, on_delete=models.CASCADE)
    dates = ArrayField(models.DateField(), default=list)

    def __str__(self):
        self.dates = list(set(self.dates)) #removing duplicate dates if any
        return f'{self.bus} schedule'
    
def get_upcoming_day(target_day):
    today = datetime.now()
    target = day_map[target_day]
    if target > today.weekday():
        a = target - today.weekday()
    elif target <= today.weekday():
        a = 7 + target - today.weekday()
    return (today + timedelta(days = a))
    

def update_schedule():
    from home.models import bus
    print("Updating schedule....")
    buses = bus.objects.all()
    for bus_obj in buses:
        newDates = [get_upcoming_day(day) for day in bus_obj.operating_days]
        bus_obj.schedule.dates = newDates
        bus_obj.schedule.save()
