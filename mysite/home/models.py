from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# Create your models here.

class bus(models.Model):
    city1 = models.CharField(max_length = 30)
    city2 = models.CharField(max_length = 30)
    seats_total = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    seats_available = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    timing = models.DateTimeField()
    
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
