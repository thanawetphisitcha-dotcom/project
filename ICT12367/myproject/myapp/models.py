from django.db import models
from django.contrib.auth.models import User

# 1. ตารางเก็บข้อมูล "โต๊ะอาหาร"
class Table(models.Model):
    STATUS_CHOICES = (
        ('available', 'ว่าง / พร้อมใช้งาน'),
        ('maintenance', 'ปรับปรุง / ซ่อมแซม'),
        ('closed', 'ปิดให้บริการ'),
    )
    number = models.CharField(max_length=10, unique=True, verbose_name="หมายเลขโต๊ะ")
    seats = models.IntegerField(verbose_name="จำนวนที่นั่ง", default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="สถานะ")
    is_active = models.BooleanField(default=True, verbose_name="เปิดใช้งาน")

    def __str__(self):
        return f"โต๊ะ {self.number} ({self.seats} ที่นั่ง)"

# 2. ตารางเมนูอาหาร (สำหรับระบบ Admin)
class FoodMenu(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อเมนู")
    price = models.IntegerField(verbose_name="ราคา")
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True, verbose_name="รูปภาพอาหาร")
    is_available = models.BooleanField(default=True, verbose_name="พร้อมขาย (มีของ)")

    def __str__(self):
        return self.name

# 3. ตารางเก็บข้อมูล "การจอง"
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'รอเข้าใช้งาน'),
        ('completed', 'สำเร็จ (ทานเสร็จแล้ว)'),
        ('cancelled', 'ยกเลิกการจอง'),
    )
    # ผูกกับ User (ดึงมาจากโค้ดชุดแรกของคุณ)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="โต๊ะที่จอง")
    name = models.CharField(max_length=100, verbose_name="ชื่อผู้จอง")
    phone = models.CharField(max_length=15, verbose_name="เบอร์โทรศัพท์")
    date = models.DateField(verbose_name="วันที่จอง", null=True, blank=True)
    time = models.TimeField(verbose_name="เวลา", null=True, blank=True)
    guests = models.IntegerField(verbose_name="จำนวนคน", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะการจอง")
    
    # วันที่บันทึกข้อมูลการจอง (ใส่ null=True ไว้เผื่อข้อมูลเก่าที่ไม่มีฟิลด์นี้จะได้ไม่ Error)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="จองเมื่อ", null=True, blank=True)

    def __str__(self):
        return f"คุณ {self.name} - สถานะ: {self.get_status_display()}"