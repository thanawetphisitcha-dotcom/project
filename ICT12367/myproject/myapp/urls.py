from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from myapp import views

urlpatterns = [
    # --- ของระบบ Django ดั้งเดิม ---
    path('admin/', admin.site.urls),
    
    # --- หน้าของลูกค้า (User) ---
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('success/', views.success, name='success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('menu/', views.menu, name='menu'),
    
    # --- ระบบสมาชิก ---
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'), 

    # --- URLs สำหรับระบบหลังบ้าน (Admin Dashboard ที่เราสร้างใหม่) ---
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # หน้าจัดการการจอง และ เปลี่ยนสถานะ
    path('manage/bookings/', views.admin_bookings, name='admin_bookings'),
    path('manage/bookings/update/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),

    # หน้าจัดการโต๊ะ (เอา path หลอกออกแล้ว)
    path('manage/tables/', views.admin_tables, name='admin_tables'),
    path('manage/tables/add/', views.add_table, name='add_table'),
    path('manage/tables/update/<int:table_id>/', views.update_table_status, name='update_table_status'),

    # หน้าจัดการเมนูอาหาร (เอา path หลอกออกแล้ว)
    path('manage/menu/', views.admin_menu, name='admin_menu'),
    path('manage/menu/add/', views.add_menu, name='add_menu'),
    path('manage/menu/toggle/<int:menu_id>/', views.toggle_menu_status, name='toggle_menu_status'),
    path('manage/menu/delete/<int:menu_id>/', views.delete_menu, name='delete_menu'),
    path('login_success/', views.login_success, name='login_success'),
]