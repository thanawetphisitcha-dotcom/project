from django.contrib import admin
from .models import Table, Booking, FoodMenu 

# --- ตั้งค่าหน้าแสดงผลของ "โต๊ะอาหาร" ---
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    # 🌟 เพิ่ม 'status' เข้ามา เพื่อให้โชว์ว่า ว่าง/ซ่อม/ปิด
    list_display = ('number', 'seats', 'status', 'is_active')
    # 🌟 เพิ่มกรองตาม 'status' ได้ด้วย
    list_filter = ('status', 'is_active')
    search_fields = ('number',)

# --- ตั้งค่าหน้าแสดงผลของ "การจอง" ---
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # 🌟 เพิ่ม 'status' เพื่อให้โชว์ว่า รอดำเนินการ/สำเร็จ/ยกเลิก
    list_display = ('name', 'table', 'date', 'time', 'guests', 'phone', 'status')
    # 🌟 เพิ่มให้กรองตาม 'status' ได้
    list_filter = ('status', 'date', 'table')
    search_fields = ('name', 'phone')
    ordering = ('-date', '-time')

# --- ตั้งค่าหน้าแสดงผลของ "เมนูอาหาร" (ตารางใหม่) ---
@admin.register(FoodMenu)
class FoodMenuAdmin(admin.ModelAdmin):
    # ให้โชว์ชื่อ ราคา และสถานะว่าพร้อมขายไหม
    list_display = ('name', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)