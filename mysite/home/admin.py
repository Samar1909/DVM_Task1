from django.contrib import admin
from . models import bus, ticket, wallet,schedule

# Register your models here.
admin.site.register(bus)
admin.site.register(ticket)
admin.site.register(wallet)
admin.site.register(schedule)
