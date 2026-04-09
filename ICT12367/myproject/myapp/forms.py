from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ExtendedRegisterForm(UserCreationForm):
    first_name = forms.CharField(label='ชื่อจริง', max_length=100, required=True)
    last_name = forms.CharField(label='นามสกุล', max_length=100, required=True)
    email = forms.EmailField(label='อีเมล', required=True)
    phone = forms.CharField(label='เบอร์โทรศัพท์', max_length=10, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        # เราสามารถเก็บเบอร์โทรไว้ใน Profile หรือ field อื่นได้ 
        # ในขั้นตอนนี้เราจะบันทึกข้อมูลพื้นฐานก่อน
        if commit:
            user.save()
        return user