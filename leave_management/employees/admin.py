import random,string
from django.contrib import admin
from .models import Employee
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display=('first_name','last_name','email','department','designation')
    def save_model(self,request,obj,form,change):
        if not change:
            password=self.generate_random_password()
            user=User.objects.create_user(
                username=obj.email,
                email=obj.email,
                password=password,
                first_name=obj.first_name,
                last_name=obj.last_name
            )
            self.send_password_email(obj.email,password)
        
        super().save_model(request,obj,form,change)

    def generate_random_password(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


    def send_password_email(self,email,password):
        subject='Your Account Credentials'
        message=f"""
        Hello,

        Your account has been created successfully. Login credentials are as follows:

        Username: {email}
        Password: {password}

        """
        try:
            send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

class CustomUserAdmin(UserAdmin):
    pass

admin.site.unregister(User)
admin.site.register(User,CustomUserAdmin)

