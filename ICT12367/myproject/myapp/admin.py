from django.contrib import admin
from .models import Table, Booking

# --- ตั้งค่าหน้าแสดงผลของ "โต๊ะอาหาร" ---
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    # ให้โชว์คอลัมน์: เลขโต๊ะ, จำนวนที่นั่ง, และสถานะการเปิดใช้งาน
    list_display = ('number', 'seats', 'is_active')
    # เพิ่มตัวกรองด้านขวามือ ให้กดดูเฉพาะโต๊ะที่เปิด/ปิดใช้งานได้
    list_filter = ('is_active',)
    # เพิ่มช่องค้นหาด้วยเลขโต๊ะ
    search_fields = ('number',)

# --- ตั้งค่าหน้าแสดงผลของ "การจอง" ---
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # ให้โชว์คอลัมน์: ชื่อผู้จอง, โต๊ะ, วันที่, เวลา, จำนวนคน
    list_display = ('name', 'table', 'date', 'time', 'guests', 'phone')
    # เพิ่มตัวกรองด้านขวามือ ให้กรองตาม "วันที่จอง" และ "เลขโต๊ะ" ได้
    list_filter = ('date', 'table')
    # เพิ่มช่องค้นหา พิมพ์ชื่อลูกค้าหรือเบอร์โทรเพื่อหาการจองได้ทันที
    search_fields = ('name', 'phone')
    # ให้เรียงลำดับจากวันที่ล่าสุดขึ้นก่อน
    ordering = ('-date', '-time')