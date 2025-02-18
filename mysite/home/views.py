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
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError

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
        print(f'busList is {busList}')
        if len(busList) == 0:
            messages.info(request, f'Sorry No buses available at the moment')
        return render(request, 'home/handleSearch.html', {'busList': busList})
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
    

def pass_bookTicket(request, pk):
    current_bus = bus.objects.filter(id=pk).first()
    # Get number of passengers from POST or session
    num_pass = int(request.POST.get('num_pass', request.session.get('num_pass', 1)))
    
    PassengerFormSet = formset_factory(PassengerDetailForm, extra=0)
    
    if request.method == 'POST':
        # Handle add/remove passenger buttons
        existing_data = []
        formset = PassengerFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                existing_data.append(form)
        else:
            messages.error(request, "The data entered was not correct")
            return render(request, 'home/pass_bookTicket.html', {
                'formset': formset, 
                'num_pass': num_pass,
                'current_bus': current_bus
            })
        
        if 'addPassenger' in request.POST:
            num_pass += 1
            # Store in session
            request.session['num_pass'] = num_pass
            # Create new formset with updated number
            formset = PassengerFormSet(initial=existing_data)
            return render(request, 'home/pass_bookTicket.html', {
                'formset': formset, 
                'num_pass': num_pass,
                'current_bus': current_bus
            })
            
        if 'removePassenger' in request.POST:
            if num_pass > 1:
                num_pass -= 1
                request.session['num_pass'] = num_pass
                formset = PassengerFormSet(initial=existing_data)
                return render(request, 'home/pass_bookTicket.html', {
                    'formset': formset, 
                    'num_pass': num_pass,
                    'current_bus': current_bus
                })
            else:
                messages.error(request, "There should be at least 1 passenger")
        
        # Handle form submission
        if 'submitBooking' in request.POST:
            formset = PassengerFormSet(request.POST)
            if formset.is_valid():
                for form in formset:
                    print(form.cleaned_data)
                return redirect('pass_home')
            else:
                messages.error(request, "The data entered was not correct")
    else:
        # GET request
        formset = PassengerFormSet(initial=[{} for _ in range(num_pass)])
    
    return render(request, 'home/pass_bookTicket.html', {
        'formset': formset, 
        'num_pass': num_pass,
        'current_bus': current_bus
    })

      
    

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

