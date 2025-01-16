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

    employee=models.ForeignKey(User, on_delete=models.CASCADE)
    leave_duration=models.CharField(max_length=10,choices=LEAVE_DURATION_CHOICES,default='Full Day')
    leave_type=models.CharField(max_length=20,choices=LEAVE_TYPES)
    leave_date=models.DateField()
    reason=models.TextField()
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Pending')
    admin_reason=models.TextField(null=True,blank=True)
    applied_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.status})"