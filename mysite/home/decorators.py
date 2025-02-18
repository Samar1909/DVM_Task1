from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from . utils import generate_otp, verify_otp
from django.contrib.auth import logout

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
                new_user = request.user
                logout(request)
                email_otp = generate_otp()
                new_user.email_otp = email_otp
                new_user.save()
                
                send_mail(
                    'Email Verification OTP',
                    f'Your otp for email verification is {email_otp}',
                    settings.EMAIL_HOST_USER,
                    [new_user.email],
                    fail_silently = False
                    )
                print(f'Email otp {new_user.email_otp}')
                return redirect('verify_otp', user_id = new_user.pk)
                
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