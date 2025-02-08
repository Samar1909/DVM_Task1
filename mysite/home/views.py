from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from django.views.generic.edit import CreateView
from . models import *
from . decorators import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
@unauthenticated_user
def home(request):
    return render(request, template_name = "home/home.html")

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

#passenger views start here....
@login_required(login_url='login')
@allowed_users(allowed_roles=['passenger'])
def pass_home(request):
    return HttpResponse("This is passenger home")
#passenger views end here.....

#admin views start here....
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def admin_home(request):
    return render(request, 'home/admin_home.html')

@method_decorator(login_required(login_url='login'), name = 'dispatch')
@method_decorator(allowed_users(allowed_roles=['admin']), name = 'dispatch')
class admin_addBus(CreateView):
    model = bus
    fields = ['city1', 'city2', 'seats_total', 'timing']
    template_name = 'home/admin_addBus.html'
#admin views end here.....

