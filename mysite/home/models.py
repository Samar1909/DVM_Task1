from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField


day_List = [('Mon', 'Monday'),
            ('Tue', 'Tuesday'),
            ('Wed', 'Wednesday'),
            ('Thu','Thursday'),
            ('Fri', 'Friday'),
            ('Sat', 'Saturday'),
            ('Sun', 'Sunday')]

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
        

class booking(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    bus  = models.ForeignKey(bus, on_delete = models.CASCADE)
    is_booked = models.BooleanField(default = False)

class account(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10000)])
