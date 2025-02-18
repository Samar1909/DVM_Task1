from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from . models import *
from . decorators import *
from . forms import *
from . utils import generate_otp, verify_otp
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db import IntegrityError
from datetime import date
from django.template.loader import render_to_string
import time

# Create your views here.
@unauthenticated_user
def home(request):
    return render(request, template_name = "home/home.html")

class registerView(View):
    def post(self, request):
        form = registerForm(request.POST)
        if form.is_valid():
            try:
                new_user = form.save()
            except IntegrityError:
                messages.error(request, f'The user with this email already exists.')
            except Exception as e:
                messages.error(request, f'Some unexpected error has occured')
            email_otp = generate_otp()
            new_user.email_otp = email_otp
            new_user.save()

            send_mail(
                'Email Verification OTP',
                f'Your otp for email verification is {email_otp}',
                settings.EMAIL_HOST_USER,
                [form.cleaned_data.get('email')],
                fail_silently = False
                )
            print(f'Email otp {new_user.email_otp}')
            return redirect('verify_otp', user_id = new_user.pk)

        else:
            messages.error(request, f'{form.errors}')
            return redirect('register')
    def get(self, request):
        form = registerForm()
        return render(request, 'home/register.html', {'form': form})

def verify_otp_func(request, user_id):
    user = MyUser.objects.filter(id = user_id).first()
    if request.method == 'POST':
        user_otp = request.POST.get('email_otp')
        if verify_otp(user_otp, user.email_otp):
            user.is_email_verified = True
            user.email_otp = None
            user.groups.set([pass_group]) 
            user.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect('home')
        else:
            messages.error(request, f'Invalid OTP')

    return render(request, 'home/verify_otp.html')



@method_decorator(unauthenticated_user, name = 'dispatch')
class loginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            print("in if block")
            login(request, user)
            messages.success(request, f'Welcome {username}!')
            if user.groups.filter(name = 'passenger').exists():
                return redirect('pass_home')
            if user.groups.filter(name = 'admin').exists():
                return redirect('admin_home')
        else:
            print("in else block")
            messages.error(request, 'Incorrect username or password')
            return redirect('login')
    def get(self, request):
        return render(request, 'home/login.html')

def logoutView(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def handleSearch(request):
    form = searchForm(request.GET)
    if form.is_valid():
        busList = bus.objects.filter(city1__icontains = form.cleaned_data.get('city1'),
                                    city2__icontains = form.cleaned_data.get('city2'),
                                    schedule__dates__contains=[form.cleaned_data.get('date')]
                                    ).order_by('time_start')
        datestr = form.cleaned_data.get('date').isoformat()
        
        if len(busList) == 0:
            messages.info(request, f'Sorry No buses available at the moment')
        return render(request, 'home/handleSearch.html', {'busList': busList, 'datestr': datestr})
    else:
        messages.warning(request, f'Pls refine your query')
        return render(request, 'home/home.html', {'form': form})


#passenger views start here....

@login_required(login_url='login')
@allowed_users(allowed_roles=['passenger'])
def pass_home(request):
    balance = request.user.wallet.amount
    schedules = schedule.objects.all()
    form = searchForm()
    return render(request, 'home/pass_home.html', {'balance': balance, 'schedules': schedules, 'form': form})

@method_decorator(login_required(login_url='login'), name = 'dispatch')
@method_decorator(allowed_users(allowed_roles=['passenger']), name = 'dispatch')
class pass_updateWallet(View):
    def post(self, request):
        form = WalletUpdateForm(request.POST)
        user_wallet = request.user.wallet
        if form.is_valid():
            if (user_wallet.amount + form.cleaned_data.get('amount')) < 10000:
                user_wallet.amount = user_wallet.amount + form.cleaned_data.get('amount')
                user_wallet.save()
                messages.success(request, f'Rs {form.cleaned_data.get('amount')} was successfully added to your wallet. Your balance is now Rs {user_wallet.amount}')
                return redirect('pass_home')
            else:
                messages.warning(request, f"Balance can't exceed Rs 10000. Your current balance is {user_wallet.amount}")
              
        return render(request, 'home/pass_walletUpdate.html', {'form': form})
    def get(self, request):
        form = WalletUpdateForm()
        return render(request, 'home/pass_walletUpdate.html', {'form': form})
    

def pass_bookTicket(request, pk, datestr):
    current_bus = bus.objects.filter(id=pk).first()
    
    current_date = date.fromisoformat(datestr)
    
    if request.method == 'POST':
        if 'pass_number' in request.POST:
            num_pass = int(request.POST.get('num_pass'))
            if num_pass < 1 or num_pass > 10:
                messages.error(request, f'Can only book tickets for 1 to 10 passengers at a time')
                return redirect('pass_bookTicket', pk = pk)
        
            PassengerFormSet = formset_factory(PassengerDetailForm, extra=num_pass)

            if 'submitBooking' in request.POST:
                formset = PassengerFormSet(request.POST)
                if formset.is_valid():
                    if request.user.wallet.amount > num_pass*current_bus.fare:
                        email_otp = generate_otp()

                        send_mail(
                            'Booking Confirmation',
                            f'Your otp for email confirmation is {email_otp}',
                            settings.EMAIL_HOST_USER,
                            [request.user.email],
                            fail_silently=False
                        )
                        current_ticket = ticket.objects.create(num = num_pass, 
                                            bus = current_bus, dateOfBooking = current_date, 
                                            price = num_pass*int(current_bus.fare),
                                            city1 = current_bus.city1, city2 = current_bus.city2)
                        
                        
                        if current_ticket.is_confirm == False:
                            if 'verified' in request.POST:
                                user_otp = request.POST.get('email_otp')
                                if verify_otp(email_otp, user_otp):
                                    current_ticket.is_confirm = True
                            else:
                                return render(request, 'home/verify_otp.html')
                        
                        if current_ticket.is_confirm:
                            for form in formset:
                                    new_instance = form.save(commit = False)
                                    new_instance.ticket = current_ticket
                                    new_instance.save()
                                    current_ticket.users.add(form.cleaned_data.get('user'))
                                    current_ticket.save()
                            
                            current_bus.seats_available -= num_pass
                            request.user.wallet.amount -= current_ticket.price
                            request.user.wallet.save()
                            current_bus.save()
                            for user in current_ticket.users:
                                email_context = {
                                    'username': user.username,
                                    'current_ticket': current_ticket
                                }
                                html_content = render_to_string("pass_bookTicketTemplate.html", email_context)
                                text_content = render_to_string("pass_bookTicketTemplateText.txt", email_context)
                                msg = EmailMultiAlternatives(
                                        "Booking Confirmation",
                                        text_content,
                                        settings.EMAIL_HOST_USER,
                                        user.email,
                                        headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
                                    )
                                msg.attach_alternative(html_content, "text/html")
                                msg.send()

                            messages.success(request, f'Your ticket was booked successfully! Rs{current_ticket.price} was deducted from your account.')
                            messages.success(request, "A confirmation email is sent to the accounts of all the users")
                            return redirect('home')
                        
                            
                    else:
                        messages.error(request, f'Garib Saala')
                                
                else:
                    messages.error(request, "The data entered was not valid")

                return render(request, 'home/pass_bookTicket.html', {'formset': formset, 'num_pass': num_pass}) 
            
            formset = PassengerFormSet()
            return render(request, 'home/pass_bookTicket.html', {'formset': formset, 'num_pass': num_pass})           
                 
    if request.method == 'GET':
        num_pass = 0
        return render(request, 'home/pass_bookTicket.html', {'num_pass': num_pass})  

# class pass_ticketConfirm(View):
#     def post(self, request, ticket_id):

#         user_otp = request.POST.get('email_otp') 
#         if verify_otp()
#     def get(self, request, ticket_id):
#         return render(request, 'home/verify_otp.html')    
   


        
        
def upcomingTripsView(request):
    tickets = request.user.ticket_set.filer(dateOfBooking__gt = timezone.now()).order_by('dateOfBooking')  
    return render(request, 'home/upcomingTripView.html')    

   
    

#passenger views end here.....

#admin views start here....
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def admin_home(request):
    schedules = schedule.objects.all()
    form = searchForm()
    return render(request, 'home/admin_home.html', {'schedules': schedules, 'form': form})



@method_decorator(login_required(login_url='login'), name = 'dispatch')
@method_decorator(allowed_users(allowed_roles=['admin']), name = 'dispatch')
class admin_addBus(View):
    def post(self, request):
        form  = AddBusForm(request.POST)
        if form.is_valid():
            form.save()
            bus_name = form.cleaned_data.get('name')
            messages.success(request, f'{bus_name} was added successfully!')
            return redirect('admin_home')
        else:
            messages.error(request, f'The data entered was not correct')
            return render(request, 'home/admin_addBus.html', {'form': form})

    def get(self, request):
        form = AddBusForm()
        return render(request, 'home/admin_addBus.html', {'form': form})

@method_decorator(login_required(login_url='login'), name = 'dispatch')
@method_decorator(allowed_users(allowed_roles=['admin']), name = 'dispatch')
class admin_busListView(ListView):
    model = bus
    template_name = 'home/admin_busListView.html'
    context_object_name = 'buses'

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def admin_busDetailView(request, pk):
    current_bus = None
    if bus.objects.filter(id = pk).exists():
        current_bus = bus.objects.filter(id = pk).first()
    return render(request, 'home/admin_busDetailView.html', {'bus': current_bus})

@method_decorator(login_required(login_url='login'), name = 'dispatch')
@method_decorator(allowed_users(allowed_roles=['admin']), name = 'dispatch')
class admin_busUpdateView(View):
    def post(self, request, pk):
        current_bus = bus.objects.get(id = pk)
        form  = AddBusForm(request.POST, instance = current_bus)
        if form.is_valid():
            form.save()
            bus_name = form.cleaned_data.get('name')
            messages.success(request, f'{bus_name} was updated successfully!')
            return redirect('admin_busDetailView', pk = pk)
        else:
            messages.error(request, f'The data entered was not correct')
            return render(request, 'home/admin_busUpdateView.html', {'form': form})

    def get(self, request, pk):
        current_bus = bus.objects.get(id = pk)
        form = AddBusForm(instance = current_bus)
        return render(request, 'home/admin_busUpdateView.html', {'form': form})

# admin views end here.....

