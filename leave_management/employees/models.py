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
    employee_name=models.CharField(max_length=255,blank=True,null=True),#retaining name
    employee_email=models.EmailField(blank=True,null=True),#retaining email
    leave_duration=models.CharField(max_length=10,choices=LEAVE_DURATION_CHOICES,default='Full Day')
    leave_type=models.CharField(max_length=20,choices=LEAVE_TYPES)
    leave_date=models.DateField()
    reason=models.TextField()
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Pending')
    admin_reason=models.TextField(null=True,blank=True)
    applied_date=models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
       #if employee exists we will store their name and email in the record
       if self.employee:
           self.employee_name=f"{self.employee.first_name} {self.employee.last_name}"
           self.employee_email=self.employee.email
       super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee.username or 'Unknown Employee'} - {self.leave_type} ({self.status})"