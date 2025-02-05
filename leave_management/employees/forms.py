from django import forms
from .models import LeaveApplication,Employee
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False,widget=forms.CheckboxInput(),label="Remember Me")


class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['leave_duration','leave_type','leave_date','reason']
        widgets ={
            'leave_date': forms.DateInput(attrs={'type':'date'}),
        }

from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self,email):
        active_users=super().get_users(email)
        return active_users.filter(is_active=True)
    
class BankDetailsForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields=['bank_account_number','bank_name','ifsc_code']
        widgets={
            'bank_account_number': forms.TextInput(attrs={'class':'form-control'}),
            'bank_name':forms.TextInput(attrs={'class':'form-control'}),
            'ifsc_code':forms.TextInput(attrs={'class':'form-control'}),
        }

