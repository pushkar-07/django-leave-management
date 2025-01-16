from django import forms
from .models import LeaveApplication


# class LoginForm(forms.Form):
#     username=forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 'class':'form-control',
#                 # 'placeholder':'email'
#             }
#         )
#     )
#     password=forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 'class':'form-control'
                
#             }
#         )
#     )


class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['leave_duration','leave_type','leave_date','reason']
        widgets ={
            'leave_date': forms.DateInput(attrs={'type':'date'}),
        }

