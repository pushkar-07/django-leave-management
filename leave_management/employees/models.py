from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

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
    bonus_amount=models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    bank_account_number=models.CharField(max_length=50,blank=True,null=True)
    bank_name=models.CharField(max_length=100,blank=True,null=True)
    ifsc_code=models.CharField(max_length=20,blank=True,null=True)
    # supervisor = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL)

    def calculate_bonus(self):
        """Convert extra leaves (above 22) into money."""
        if self.leave_balance > 22:
            extra_leaves=self.leave_balance-22
            bonus_per_leave = Decimal('500.00')
            self.bonus_amount += (extra_leaves * bonus_per_leave)
            self.leave_balance=22
            self.save()
            return self.bonus_amount
        return Decimal('0.00')

    def update_annual_leaves(self):
        """Method to be called annually to process leave conversion"""
        return self.calculate_bonus()    

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
        if not self.pk:  # If this is a new application
        # Check for existing active leave applications
            existing_leave = LeaveApplication.objects.filter(
                employee=self.employee,
                leave_date=self.leave_date,
                status__in=['Pending', 'Approved']  # Only check for active leaves
            ).exists()
            if existing_leave:
                raise ValueError("An active leave application already exists for this date.")
        # deduct leaves if status is pending for new application
            if self.status == 'Pending':
                employee = Employee.objects.filter(email=self.employee_email).first()
                if employee and employee.leave_balance > 0:
                    employee.leave_balance -= 1
                    employee.save()
                else:
                    raise ValueError("Insufficient leave balance. Cannot apply for leave.")
        else:
        # This is an existing application being updated
            original = LeaveApplication.objects.get(pk=self.pk)
            if original.status == 'Pending' and self.status == 'Rejected':  # rejection case
            # crediting leaves back
                employee = Employee.objects.filter(email=self.employee.email).first()
                if employee:
                    if original.status == 'Pending':
                        employee.leave_balance += 1
                        employee.save()

        super().save(*args, **kwargs)
    

    def __str__(self):
        return f"{self.employee.username or 'Unknown Employee'} - {self.leave_type} ({self.status})"

class BonusClaim(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='bonus_claim')
    amount =models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=20,choices=[('Pending','Pending'),('Approved','Approved'),('Rejected','Rejected'),('Paid','Paid')],default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.TextField(blank=True,null=True)
    admin_remarks = models.CharField(max_length=100,blank=True,null=True)
    transaction_id=models.CharField(max_length=100,blank=True,null=True)
    original_leave_balance = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return f"{self.employee.first_name} - ₹{self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.original_leave_balance = self.employee.leave_balance
        if self.pk:
            # Get the original object before changes
            orig = BonusClaim.objects.get(pk=self.pk)
            #if status changed to rejected
            if orig.status != 'Rejected' and self.status == 'Rejected':
                #restoring original leave balance
                self.employee.leave_balance = self.original_leave_balance
                self.employee.bonus_amount = Decimal('0.00')
                self.employee.save()

            # If status is changed to paid
            elif orig.status != 'Paid' and self.status == 'Paid':
                # Reset employee's bonus amount to 0 only after payment
                self.employee.bonus_amount = Decimal('0.00')
                self.employee.save()
                
        super().save(*args, **kwargs)

class Notification(models.Model):
    recipient = models.ForeignKey(User,on_delete=models.CASCADE) # admin who receives the notificatoin
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"
