from django import forms
from django.forms import ModelForm
from . models import bus, passDetails, day_List, MyUser
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class registerForm(UserCreationForm):
    email = forms.EmailField(
        widget = forms.EmailInput(attrs={'type': 'email', 'class': 'form-control'})
        )
    username = forms.CharField(
        widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        )
    password1 = forms.CharField(
        widget = forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control'})
        )
    password2 = forms.CharField(
        widget = forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control'})
        )

    class Meta:
        model = MyUser
        fields = ['username', 'email', 'password1', 'password2']

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
        max_length=100,
        )
    
    date = forms.DateField(
        label = "Date",
        widget = forms.DateInput(attrs = {'type': 'date', 'placeholder': 'YYYY-MM-DD'})
    )
