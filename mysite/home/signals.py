from . models import wallet
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