from django.contrib import admin
from django.urls import path, include
from . import views
from . views import *

urlpatterns = [
    path('', views.home, name = 'home'),
    path('register/', registerView.as_view(), name = "register"),
    path('register/verify_otp/<int:user_id>', views.verify_otp_func, name = "verify_otp"),
    path('login/', loginView.as_view(), name = 'login'),
    path('logout/', views.logoutView, name = 'logout'),
    path('search/', views.handleSearch, name = "search"),
    path('passenger/home', views.pass_home, name = 'pass_home'),
    path('passenger/updateWallet', pass_updateWallet.as_view(), name = "pass_updateWallet"),
    path('passenger/buses/<int:pk>/bookTicket/<str:datestr>', views.pass_preBookTicket, name = "pass_preBookTicket"),
    path('passenger/buses/<int:pk>/bookTicket/<str:datestr>/<int:num_pass>', views.pass_bookTicket, name = 'pass_bookTicket'),
    path('passenger/buses/<int:pk>/bookTicket/<int:ticket_id>/verify', views.pass_bookTicketVerifyOtp, name = 'pass_bookTicketVerifyOtp'),
    path('passenger/upcomingTrips', views.pass_upcomingTripsView, name = "pass_upcomingTripsview"),
    path('passenger/tickets/<int:pk>/', views.pass_ticketDetailView, name = "pass_ticketDetail"),
    path('passenger/tickets/<int:pk>/cancel', views.pass_cancelTicket, name = "pass_cancelTicket"),
    path('passenger/tickets/<int:pk>/update/passengerDetails', views.pass_updatePassDetails, name = "pass_updatePassDetails"),
    path('administrator/home', views.admin_home, name = "admin_home"),
    path('administrator/addBus', admin_addBus.as_view(), name = 'admin_addBus'),
    path('administrator/listOfBuses', admin_busListView.as_view(), name = "admin_busListView"),
    path('administartor/buses/<int:pk>', views.admin_busDetailView, name = "admin_busDetailView"),
    path('administartor/buses/<int:pk>/update', admin_busUpdateView.as_view(), name = "admin_busUpdateView"),
    path('administrator/buses/<int:pk>/reservation_details', views.admin_busReservationList, name = "admin_busReservationList"),
    path('administrator/buses/<int:pk>/reservation_details/export_data_to_excel/', views.admin_excelExport, name="admin_export_data_to_excel")
    # path('admin/login', admin_login.as_view(), name = 'admin_login'),
]