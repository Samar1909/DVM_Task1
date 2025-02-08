from django.contrib import admin
from django.urls import path, include
from . import views
from . views import *

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', loginView.as_view(), name = 'login'),
    path('logout/', views.logoutView, name = 'logout'),
    path('passenger/home', views.pass_home, name = 'pass_home'),
    path('administrator/home', views.admin_home, name = 'admin_home'),
    path('administrator/addBus', admin_addBus.as_view(), name = 'admin_addBus')
    # path('admin/login', admin_login.as_view(), name = 'admin_login'),
]