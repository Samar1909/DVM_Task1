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

class bus(models.Model):
    bus_number = models.IntegerField(default = 10000, blank=False, null=False, validators=[MaxValueValidator(99999), MinValueValidator(10000)])
    name = models.CharField(default = 'bus_name', blank=False, null=False, max_length=50)
    city1 = models.CharField(max_length = 30)
    city2 = models.CharField(max_length = 30)
    seats_total = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    seats_available = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    operating_days = ArrayField(
        models.CharField(max_length = 10, choices = day_List), 
        blank = False,
        null = False, 
        default = list) #default would be an empty list
    time_start = models.CharField(max_length= 4, default = '0000', blank=False, null=False, validators = [time_validator])
    time_end = models.CharField(max_length= 4, default = '0000', blank=False, null=False, validators = [time_validator])
    fare = models.PositiveIntegerField(default = 0)
        
    def __str__(self):
        return self.name

    def seats(self):
        self.seats_available = self.seats_total
    
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.seats()
        super().save(*args, **kwargs)

class booking(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    bus  = models.ForeignKey(bus, on_delete = models.CASCADE)
    is_booked = models.BooleanField(default = False)

class account(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10000)])
