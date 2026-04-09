from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import datetime, date

from .models import Table, Booking, FoodMenu
from .forms import ExtendedRegisterForm

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = ExtendedRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ล็อกอินให้ทันทีหลังสมัครเสร็จ
            
            # 🌟 [เพิ่มใหม่] เช็กสิทธิ์ User: ถ้าเป็น Admin ให้ไปหน้าจัดการโต๊ะทันที
            if user.is_staff:
                messages.success(request, "ยินดีต้อนรับท่านผู้ดูแลระบบ! เข้าสู่ระบบเรียบร้อย")
                return redirect('admin_dashboard')
            
            # ถ้าเป็นลูกค้าทั่วไป ให้ไปหน้าแรกตามเดิม
            messages.success(request, "สมัครสมาชิกและเข้าสู่ระบบเรียบร้อย!")
            return redirect('home')
    else:
        form = ExtendedRegisterForm()
    return render(request, 'register.html', {'form': form})

# ----------------------------------------------------
# ฟังก์ชันด้านล่างนี้ บังคับว่าต้องล็อกอินก่อนถึงจะใช้งานได้
# ----------------------------------------------------

@login_required(login_url='/login/')
def booking(request):
    # 🌟 แก้ไข: ดึงเฉพาะโต๊ะที่ status เป็น 'available' เท่านั้น
    # (ถ้าแอดมินตั้งเป็น 'closed' หรือ 'busy' โต๊ะจะหายไปจากหน้านี้ทันที)
    tables = Table.objects.filter(status='available')
    
    booking_user = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'email': request.user.email,
        'phone': getattr(request.user, 'phone', '')
    }
    return render(request, 'booking.html', {'tables': tables, 'booking_user': booking_user})


@login_required(login_url='/login/')
def success(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date_str = request.POST.get('date')
        time = request.POST.get('time')
        guests = request.POST.get('guests')
        table_id = request.POST.get('table_id')

        selected_table = get_object_or_404(Table, id=table_id)

        # -----------------------------------------
        # 🚨 [แก้ไข] ด่านตรวจที่ 0: เช็กว่าสถานะยังเป็น 'available' อยู่ไหม
        # -----------------------------------------
        if selected_table.status != 'available':
            tables = Table.objects.filter(status='available')
            error_msg = f"❌ ขออภัยครับ โต๊ะ {selected_table.number} ปิดปรับปรุงหรือติดจองอยู่ โปรดเลือกโต๊ะอื่นครับ"
            return render(request, 'booking.html', {'tables': tables, 'error_message': error_msg})

        # -----------------------------------------
        # 🚨 ด่านตรวจที่ 1: ห้ามจองย้อนหลัง
        # -----------------------------------------
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if booking_date < date.today():
            tables = Table.objects.filter(status='available')
            error_msg = "❌ ขออภัยครับ ไม่สามารถจองโต๊ะย้อนหลังได้"
            return render(request, 'booking.html', {'tables': tables, 'error_message': error_msg})

        # -----------------------------------------
        # 🚨 ด่านตรวจที่ 2: เช็กการจองซ้ำในวัน/เวลาเดียวกัน
        # -----------------------------------------
        is_booked = Booking.objects.filter(table=selected_table, date=date_str, time=time).exists()
        if is_booked:
            tables = Table.objects.filter(status='available')
            error_msg = f"ขออภัยครับ โต๊ะ {selected_table.number} เวลานี้ถูกจองไปแล้ว"
            return render(request, 'booking.html', {'tables': tables, 'error_message': error_msg})

        # บันทึกการจอง
        Booking.objects.create(
            user=request.user,  
            name=name, phone=phone, date=date_str, time=time, 
            guests=guests, table=selected_table
        )
        return render(request, 'success.html')
    
    return redirect('home')

@login_required(login_url='/login/')
def my_bookings(request):
    # เปลี่ยนจากการดึงทั้งหมด เป็นการเอาเฉพาะการจองที่ user ตรงกับคนที่ล็อกอินอยู่
    bookings = Booking.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required(login_url='/login/')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # สั่งลบข้อมูลออกจากฐานข้อมูล
    booking.delete()
    
    # --- 🌟 [เพิ่มใหม่] สั่งให้ระบบเตรียมข้อความแจ้งเตือนสีเขียว (Success) ---
    messages.success(request, "ยกเลิกการจองโต๊ะเรียบร้อยแล้วครับ!")
    
    # ลบเสร็จให้เด้งกลับไปที่หน้าประวัติการจองเหมือนเดิม
    return redirect('my_bookings')

def logout_view(request):
    logout(request) # ล้าง Session ของ User ออกจากระบบ
    messages.success(request, "ออกจากระบบเรียบร้อยแล้ว!")
    return redirect('home')


def menu(request):
    # 1. รับค่าที่ลูกค้าพิมพ์มาจากหน้าเว็บเหมือนเดิม
    search_query = request.GET.get('search', '')
    max_price = request.GET.get('max_price', '')

    # 2. ให้ food_items เท่ากับ เมนูใน Database ที่พร้อมขาย (is_available=True)
    # เราไม่ต้องพิมพ์ dict ยาวๆ แล้ว ดึงมาจากที่แอดมินเพิ่มไว้ได้เลย!
    food_items = FoodMenu.objects.filter(is_available=True).order_by('-id')
    
    # 3. เริ่มกรองข้อมูลด้วยคำสั่งของ Django (ORM)
    if search_query:
        # __icontains แปลว่า "มีคำนี้ซ่อนอยู่หรือไม่" (ไม่สนพิมพ์เล็กพิมพ์ใหญ่)
        food_items = food_items.filter(name__icontains=search_query)
    
    if max_price:
        # __lte แปลว่า "น้อยกว่าหรือเท่ากับ" (Less Than or Equal)
        food_items = food_items.filter(price__lte=int(max_price))

    return render(request, 'menu.html', {
        'food_items': food_items,
        'search_query': search_query,
        'max_price': max_price
    })



@login_required(login_url='/login/')
def edit_booking(request, booking_id):
    # 🌟 เพิ่ม user=request.user เข้าไป เพื่อป้องกันคนอื่นมาแอบแก้การจองของเรา
    booking = get_object_or_404(Booking, id=booking_id, user=request.user) 
    
    if request.method == 'POST':
        # รับค่าจากฟอร์มและบันทึก
        booking.name = request.POST.get('name')
        booking.phone = request.POST.get('phone')
        booking.save()
        
        # เพิ่มแจ้งเตือนสีเขียวสักนิดให้ดูโปรขึ้น
        messages.success(request, "แก้ไขข้อมูลการจองเรียบร้อยแล้ว!")
        return redirect('my_bookings') # แก้เสร็จให้กลับไปหน้าประวัติ
        
    return render(request, 'edit_booking.html', {'booking': booking})




def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='/')
def admin_dashboard(request):
    pending_bookings = Booking.objects.count()
    # 🌟 แก้ไข: นับเฉพาะโต๊ะที่ status เป็น 'available'
    available_tables = Table.objects.filter(status='available').count() 
    total_menus = FoodMenu.objects.count()
    recent_bookings = Booking.objects.all().order_by('-id')[:5]

    context = {
        'pending_bookings': pending_bookings,
        'available_tables': available_tables,
        'total_menus': total_menus,
        'recent_bookings': recent_bookings
    }
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(is_admin, login_url='/')
def admin_bookings(request):
    # 1. รับค่าค้นหาและตัวกรองจากฟอร์ม
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # 2. ดึงข้อมูลการจองทั้งหมด เรียงจากใหม่ไปเก่า
    bookings = Booking.objects.all().order_by('-date', '-time')

    # 3. ถ้ามีการพิมพ์ค้นหา (ชื่อ หรือ เบอร์โทร)
    if search_query:
        bookings = bookings.filter(
            name__icontains=search_query
        ) | bookings.filter(
            phone__icontains=search_query
        )

    # 4. ถ้ามีการเลือกสถานะ
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # ส่งค่าที่ค้นหากลับไปที่หน้าเว็บด้วยเพื่อให้ช่อง Input ไม่ว่างหลังกดค้นหา
    context = {
        'bookings': bookings,
        'search_query': search_query,
        'status_filter': status_filter
    }
    return render(request, 'admin_bookings.html', context)


@user_passes_test(is_admin, login_url='/')
# --- สำหรับอัปเดตสถานะการจอง ---
def update_booking_status(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        new_status = request.POST.get('status') # รับค่าสถานะที่แอดมินเลือก
        
        # อัปเดตสถานะและบันทึก
        booking.status = new_status
        booking.save()
        
        messages.success(request, f'อัปเดตสถานะการจองของคุณ {booking.name} เป็น "{booking.get_status_display()}" แล้ว!')
        
    return redirect('admin_bookings')


@user_passes_test(is_admin, login_url='/')
# --- สำหรับหน้าจัดการโต๊ะอาหาร ---
def admin_tables(request):
    # ดึงข้อมูลโต๊ะทั้งหมด เรียงตามเลขโต๊ะ
    tables = Table.objects.all().order_by('number')
    return render(request, 'admin_tables.html', {'tables': tables})

@user_passes_test(is_admin, login_url='/')
def add_table(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        seats = request.POST.get('seats')
        
        # เช็คว่ามีเลขโต๊ะนี้ในระบบหรือยัง
        if Table.objects.filter(number=number).exists():
            messages.error(request, f'โต๊ะหมายเลข {number} มีอยู่ในระบบแล้ว!')
        else:
            Table.objects.create(number=number, seats=seats)
            messages.success(request, f'เพิ่มโต๊ะ {number} สำเร็จ!')
            
    return redirect('admin_tables')

@login_required(login_url='/login/')
def booking(request):
    # 🌟 แก้ไข: ดึงเฉพาะโต๊ะที่ status เป็น 'available'
    tables = Table.objects.filter(status='available')
    
    booking_user = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'email': request.user.email,
        'phone': getattr(request.user, 'phone', '')
    }
    return render(request, 'booking.html', {'tables': tables, 'booking_user': booking_user})



@user_passes_test(is_admin, login_url='/')
# --- สำหรับหน้าจัดการเมนูอาหาร ---
def admin_menu(request):
    # ดึงเมนูทั้งหมดมาแสดง เรียงจากเมนูที่เพิ่มล่าสุด (ID มากสุด)
    menus = FoodMenu.objects.all().order_by('-id')
    return render(request, 'admin_menu.html', {'menus': menus})

@user_passes_test(is_admin, login_url='/')
def add_menu(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image') # ดึงไฟล์รูปภาพมา
        
        FoodMenu.objects.create(name=name, price=price, image=image)
        messages.success(request, f'เพิ่มเมนู "{name}" สำเร็จ!')
            
    return redirect('admin_menu')

@user_passes_test(is_admin, login_url='/')
def toggle_menu_status(request, menu_id):
    menu = get_object_or_404(FoodMenu, id=menu_id)
    # สลับสถานะ (ถ้า True ให้เป็น False, ถ้า False ให้เป็น True)
    menu.is_available = not menu.is_available
    menu.save()
    status = "พร้อมขาย" if menu.is_available else "หมดชั่วคราว"
    messages.success(request, f'อัปเดตสถานะเมนู "{menu.name}" เป็น "{status}" แล้ว!')
    return redirect('admin_menu')

@user_passes_test(is_admin, login_url='/')
def delete_menu(request, menu_id):
    menu = get_object_or_404(FoodMenu, id=menu_id)
    menu_name = menu.name
    menu.delete()
    messages.success(request, f'ลบเมนู "{menu_name}" ออกจากระบบแล้ว!')
    return redirect('admin_menu')


@user_passes_test(is_admin, login_url='/')
def update_table_status(request, table_id):
    if request.method == 'POST':
        table = get_object_or_404(Table, id=table_id)
        new_status = request.POST.get('status')
        table.status = new_status
        table.save()
        messages.success(request, f'อัปเดตสถานะโต๊ะ {table.number} เรียบร้อยแล้ว!')
    return redirect('admin_tables')

@login_required
def login_success(request):
    """ คัดแยก User หลังจากล็อกอินผ่านหน้า Login ปกติ """
    if request.user.is_staff:
        return redirect('admin_dashboard') # ถ้าเป็นแอดมิน ส่งไปหลังบ้าน
    else:
        return redirect('home') # ถ้าเป็นลูกค้า ส่งไปหน้าแรก