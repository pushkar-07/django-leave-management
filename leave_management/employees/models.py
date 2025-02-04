from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15,default="N/A")
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=10,default="Not Assigned")
    date_joined=models.DateField(default="2024-12-01")
    leave_balance=models.IntegerField(default=2)
    is_active=models.BooleanField(default=True)
    # supervisor = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class LeaveApplication(models.Model):
    LEAVE_TYPES = [
        ('Sick','Sick Leave'), # idhar (db_value,display_value)
        ('Casual','Casual Leave'),
        ('Other','Other'),
    ]
    LEAVE_DURATION_CHOICES=[
        ('Full Day','Full Day'),
        ('Half Day','Half Day'),
    ]

    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected'),
    ]

    employee=models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True,related_name='leave_applications')#new
    employee_name=models.CharField(max_length=255,blank=True,null=True)#retaining name
    employee_email=models.EmailField(blank=True,null=True)#retaining email
    leave_duration=models.CharField(max_length=10,choices=LEAVE_DURATION_CHOICES,default='Full Day')
    leave_type=models.CharField(max_length=20,choices=LEAVE_TYPES)
    leave_date=models.DateField()
    reason=models.TextField()
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Pending')
    admin_reason=models.TextField(null=True,blank=True)
    applied_date=models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and LeaveApplication.objects.filter(employee=self.employee,leave_date=self.leave_date).exists():
            raise ValueError("Leave application already exists for this date.")
        if self.pk:
           original = LeaveApplication.objects.get(pk=self.pk)
           if original.status == 'Pending' and self.status == 'Rejected': #rejection case
               #crediting leaves back
               employee = Employee.objects.filter(email=self.employee.email).first()
               if employee:
                   employee.leave_balance += 1
                   employee.save()
        else:
            # deduct leaves if status is pending
            if self.status == 'Pending':
                employee=Employee.objects.filter(email=self.employee_email).first()
                if employee and employee.leave_balance > 0:
                    employee.leave_balance -= 1
                    employee.save()
                else:
                    raise ValueError("Insufficient leave balance. Cannot apply for leave.")
        super().save(*args, **kwargs)
    

    def __str__(self):
        return f"{self.employee.username or 'Unknown Employee'} - {self.leave_type} ({self.status})"