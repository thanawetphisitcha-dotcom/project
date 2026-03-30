# urls.py
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('success/', views.success, name='success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    path('logout/', views.logout_view, name='logout'), 
    path('menu/', views.menu, name='menu'),

    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
]