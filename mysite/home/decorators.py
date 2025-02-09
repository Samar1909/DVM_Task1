from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.models import Group

admin_group = Group.objects.get(name = 'admin')
pass_group = Group.objects.get(name = 'passenger')

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name = 'passenger').exists():
                return redirect('pass_home')
            elif request.user.groups.filter(name = 'admin').exists():
                return redirect('admin_home')
            else:
                request.user.groups.set([pass_group]) #I have assumed that only passengers have the ability to sign in with google
                return redirect('pass_home')
        else:
            return view_func(request, *args, **kwargs)
    
    return wrapper_func

def allowed_users(allowed_roles = []):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("You are not authorised to view this page")
                
        return wrapper_func
    return decorator