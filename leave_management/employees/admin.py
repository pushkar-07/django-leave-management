import random,string
from django.contrib import admin
from .models import Employee,LeaveApplication,BonusClaim
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display=('first_name','last_name','email','department','designation')
    list_filter=('is_active',)
    
    def save_model(self,request,obj,form,change):
        #checking if the employee was previously inactive(deleted)
        was_inactive =False
        if obj.pk:
            old_obj=Employee.objects.get(pk=obj.pk)
            was_inactive=not old_obj.is_active

# if the employee is readded or is a new employee
        if not change or was_inactive:
            user = User.objects.filter(email=obj.email).first() # is user already exists
            if user is None:
                #creating a new user
                password=self.generate_random_password()
                user=User.objects.create_user(
                    username=obj.email,
                    email=obj.email,
                    password=password,
                    first_name=obj.first_name,
                    last_name=obj.last_name
                )
                self.send_password_email(obj.email,password)
            else:
                #reactivating old user
                user.is_active=True
                user.first_name=obj.first_name
                user.last_name=obj.last_name
                user.save()
    # new password is sent
                password=self.generate_random_password()
                user.set_password(password)
                user.save()
                self.send_password_email(obj.email,password)
            #linking back to leave applications if any present    
            LeaveApplication.objects.filter(
                employee_email=obj.email,
                employee=None
            ).update(employee=user)

        obj.is_active = True
        super().save_model(request,obj,form,change)

    def delete_model(self, request, obj):
        try:
            user = User.objects.filter(email=obj.email).first()
            if user:
                user.is_active =False
                user.set_unusable_password()
                user.save()
            LeaveApplication.objects.filter(employee=obj,status__in=['Pending'].update(status='Cancelled'))    
        except Exception as e:
            print(f"Error deactivating user: {e}")
            
        obj.is_active = False    
        obj.save()

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

@admin.register(BonusClaim)
class BonusClaimAdmin(admin.ModelAdmin):
    list_display=('employee','amount','status','created_at')
    list_filter=('status',)
    actions = ['approve_claims']

    def approve_claims(self,request,queryset):
        queryset.update(status='Approved')
        self.message_user(request,"Selected claims have been approved!")
    
    approve_claims.short_description ="Approve selected bonus claims"
