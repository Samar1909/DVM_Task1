from django import forms
from django.forms import ModelForm
from . models import *

class AddBusForm(ModelForm):
    operating_days = forms.MultipleChoiceField(choices = day_List, widget = forms.CheckboxSelectMultiple)
    class Meta:
        model = bus
        fields = ['bus_number', 'name', 'city1', 'city2', 'seats_total', 'operating_days', 'time_start', 'time_end', 'fare']