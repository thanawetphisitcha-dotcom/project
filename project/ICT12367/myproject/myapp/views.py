from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Table, Booking
from datetime import datetime, date
from .forms import ExtendedRegisterForm

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = ExtendedRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # ล็อกอินให้ทันทีหลังสมัครเสร็จ
            messages.success(request, "สมัครสมาชิกและเข้าสู่ระบบเรียบร้อย!")
            return redirect('home') # ส่งไปหน้าแรกเลย
    else:
        form = ExtendedRegisterForm()
    return render(request, 'register.html', {'form': form})

# ----------------------------------------------------
# ฟังก์ชันด้านล่างนี้ บังคับว่าต้องล็อกอินก่อนถึงจะใช้งานได้
# ----------------------------------------------------

@login_required(login_url='/login/')
def booking(request):
    tables = Table.objects.all()
    # เปลี่ยนชื่อตัวแปรตรงนี้เป็น booking_user
    booking_user = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'email': request.user.email,
        'phone': getattr(request.user, 'phone', '')
    }
    # ส่งตัวแปรชื่อ booking_user ไปแทน
    return render(request, 'booking.html', {'tables': tables, 'booking_user': booking_user})


@login_required(login_url='/login/')
def success(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date_str = request.POST.get('date') # รับค่ามาเป็นชื่อ date_str
        time = request.POST.get('time')
        guests = request.POST.get('guests')
        table_id = request.POST.get('table_id')

        # -----------------------------------------
        # 🚨 ด่านตรวจที่ 1: ห้ามจองย้อนหลัง
        # -----------------------------------------
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if booking_date < date.today():
            tables = Table.objects.filter(is_active=True)
            error_msg = "❌ ขออภัยครับ ไม่สามารถจองโต๊ะย้อนหลังได้ โปรดเลือกวันที่เป็นวันนี้หรือวันล่วงหน้าครับ"
            return render(request, 'booking.html', {'tables': tables, 'error_message': error_msg})
        # -----------------------------------------

        selected_table = Table.objects.get(id=table_id)
        
        # -----------------------------------------
        # ด่านตรวจที่ 2: โต๊ะโดนจองไปหรือยัง?
        # (แก้ตรงนี้ให้ใช้ date_str แทน date)
        # -----------------------------------------
        is_booked = Booking.objects.filter(table=selected_table, date=date_str, time=time).exists()

        if is_booked:
            tables = Table.objects.filter(is_active=True)
            error_msg = f"ขออภัยครับ โต๊ะ {selected_table.number} ในวันที่ {date_str} เวลา {time} น. ถูกจองไปแล้ว โปรดเลือกโต๊ะหรือเวลาอื่นครับ"
            return render(request, 'booking.html', {'tables': tables, 'error_message': error_msg})

        # ถ้าผ่านทุกด่าน ก็สั่งบันทึกข้อมูลได้เลย
        # (แก้ตรงนี้ให้ใช้ date_str เช่นกัน)
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
    food_items = [
        # 🌟 แก้ราคาให้เป็นตัวเลขล้วน (Integer) ไม่มีลูกน้ำ ไม่มี ' '
        {'name': 'สเต็กเนื้อวากิวพรีเมียม', 'price': 1290, 'img': 'images/menu1.jpg'},
        {'name': 'ซี่โครงแกะย่างสมุนไพร', 'price': 950, 'img': 'images/menu2.jpg'},
        {'name': 'พาสต้าล็อบสเตอร์ซอสทรัฟเฟิล', 'price': 850, 'img': 'images/menu3.jpg'},
        {'name': 'สลัดแซลมอนรมควัน', 'price': 320, 'img': 'images/menu4.jpg'},
        {'name': 'ซุปเห็ดทรัฟเฟิลเข้มข้น', 'price': 250, 'img': 'images/menu5.jpg'},
        {'name': 'เป็ดอบซอสเบอร์รี่', 'price': 680, 'img': 'images/menu6.jpg'},
        {'name': 'หอยเชลล์ฮอกไกโดย่าง', 'price': 550, 'img': 'images/menu7.jpg'},
        {'name': 'สปาเก็ตตี้คาโบนาร่าต้นตำรับ', 'price': 380, 'img': 'images/menu8.jpg'},
        {'name': 'บีฟเวลลิงตัน', 'price': 990, 'img': 'images/menu9.jpg'},
        {'name': 'ไก่ตุ๋นไวน์แดง', 'price': 590, 'img': 'images/menu10.jpg'},
        {'name': 'กุ้งล็อบสเตอร์เทอร์มิดอร์', 'price': 1990, 'img': 'images/menu11.jpg'},
        {'name': 'ไวน์แดงคัดพิเศษ', 'price': 1500, 'img': 'images/menu12.jpg'},
    ]
    
    # 1. รับค่าที่ลูกค้าพิมพ์มาจากหน้าเว็บ
    search_query = request.GET.get('search', '')
    max_price = request.GET.get('max_price', '')

    # 2. ให้ filtered_food เท่ากับเมนูทั้งหมดเป็นค่าเริ่มต้น
    filtered_food = food_items
    
    # 3. เริ่มกรองข้อมูล
    if search_query:
        filtered_food = [item for item in filtered_food if search_query.lower() in item['name'].lower()]
    
    if max_price:
        # ตอนนี้ item['price'] เป็นตัวเลขแล้ว เลยเอามาเทียบกับ int(max_price) ได้เลย
        filtered_food = [item for item in filtered_food if item['price'] <= int(max_price)]

    return render(request, 'menu.html', {
        'food_items': filtered_food,
        'search_query': search_query,
        'max_price': max_price
    })



def edit_booking(request, booking_id):
    # ดึงข้อมูลการจองที่ต้องการแก้ตาม ID
    booking = get_object_or_404(Booking, id=booking_id) 
    
    if request.method == 'POST':
        # รับค่าจากฟอร์มและบันทึก
        booking.name = request.POST.get('name')
        booking.phone = request.POST.get('phone')
        booking.save()
        return redirect('my_bookings') # แก้เสร็จให้กลับไปหน้าประวัติ
        
    return render(request, 'edit_booking.html', {'booking': booking})
