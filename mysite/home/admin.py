from django.contrib import admin
from . models import bus, ticket, wallet

# Register your models here.
admin.site.register(bus)
admin.site.register(ticket)
admin.site.register(wallet)
