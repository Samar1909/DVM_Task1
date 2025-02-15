from django import forms
from django.forms import ModelForm
from . models import bus, passDetails, day_List
from django.core.validators import MaxValueValidator

class AddBusForm(ModelForm):
    operating_days = forms.MultipleChoiceField(choices = day_List, widget = forms.CheckboxSelectMultiple)
    class Meta:
        model = bus
        fields = ['bus_number', 'name', 'city1', 'city2', 'seats_total', 'operating_days', 'time_start', 'time_end', 'fare']

class PassengerDetailForm(ModelForm):
    class Meta:
        model = passDetails
        fields = ['user', 'fname', 'lname', 'age']


class WalletUpdateForm(forms.Form):
    amount = forms.DecimalField(
        validators=[MaxValueValidator(10000)],
        label="Amount To Add",
        widget =forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount'})  
    )

class searchForm(forms.Form):
    city1 = forms.CharField(
        label = "From",
        max_length = 100
    )
    city2 = forms.CharField(
        label="To",
        max_length=100)
    
    date = forms.DateField(
        label = "Date",
        widget = forms.DateInput()
    )

