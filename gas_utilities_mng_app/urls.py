from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.start_fun),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_registration, name='user_registration'),
    path('home/',views.home,name='home_form'),
    path('admin_home/',views.admin_home,name='admin_home_form'),
    path("add_connection/",views.add_connection,name="add_connection"),
    path("fetch_dashboard_data/",views.fetch_dashboard_data,name="fetch_dashboard_data"),
    path("fetch_booking_data/",views.booking_page,name='fetch_booking_data'),
    path("booking_data/",views.booking_data,name='booking_data'),
    path("admin_connection/",views.admin_view_connection,name="admin_connection"),
    path("view_connection/<int:connection_id>",views.admin_connection_details,name="view_connection"),
    path("admin_booking/",views.admin_view_booking,name="admin_booking"),
    path("view_booking/<int:booking_no>",views.admin_confirm_booking,name="view_booking"),
    path("logout/",views.logout,name="logout"),

]
