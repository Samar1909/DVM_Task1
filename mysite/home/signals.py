from . models import wallet, bus, schedule, get_upcoming_day
from django.contrib.auth.models import User
from django.db.models.signals import post_save

def create_wallet(sender, instance, created, **kwargs):
    if created:
        wallet.objects.create(user = instance)
        print(f'Wallet created for {instance.username}')

post_save.connect(create_wallet, sender=User)

def update_wallet(sender, instance, created, **kwargs):
    if created == False:
        instance.wallet.save()
        print(f'Wallet Updated for {instance.username}')

post_save.connect(update_wallet, sender=User)

def create_schedule(sender, instance, created, **kwargs):
    if created:
        schedule.objects.create(bus = instance)
        # newDates = [get_upcoming_day(day) for day in instance.operating_days]
        # instance.schedule.dates = newDates
        # instance.schedule.save()
        print(f'schedule created for {instance.name}')

post_save.connect(create_schedule, sender=bus)

def update_schedule(sender, instance, created, **kwargs):
    if created == False:
        schedule.objects.create(bus = instance)
        print(f'schedule created for {instance.name}')

post_save.connect(update_schedule, sender=bus)