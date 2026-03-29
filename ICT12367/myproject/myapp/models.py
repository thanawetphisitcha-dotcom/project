from django.db import models
from django.contrib.auth.models import User

# ตารางเก็บข้อมูล "โต๊ะอาหาร"
class Table(models.Model):
    number = models.CharField(max_length=10, verbose_name="เลขโต๊ะ (เช่น A1, B2)")
    seats = models.IntegerField(verbose_name="จำนวนที่นั่ง")
    is_active = models.BooleanField(default=True, verbose_name="เปิดใช้งาน")

    def __str__(self):
        return f"โต๊ะ {self.number} ({self.seats} ที่นั่ง)"

# ตารางเก็บข้อมูล "การจอง"
class Booking(models.Model):
    # 2. เพิ่มบรรทัดนี้ เพื่อผูกการจองเข้ากับบัญชีลูกค้า
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, verbose_name="โต๊ะที่จอง")
    name = models.CharField(max_length=100, verbose_name="ชื่อผู้จอง")
    phone = models.CharField(max_length=15, verbose_name="เบอร์ติดต่อ")
    date = models.DateField(verbose_name="วันที่จอง")
    time = models.TimeField(verbose_name="เวลาที่จอง")
    guests = models.IntegerField(verbose_name="จำนวนคน")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="จองเมื่อ")

    def __str__(self):
        return f"คุณ {self.name} - โต๊ะ {self.table.number if self.table else ''}"
    
# Create your models here.
