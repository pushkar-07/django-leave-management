from django.shortcuts import render
from .models import Employee
from django.shortcuts import get_object_or_404,redirect
# Create your views here.

def employee_list(request):
    employees = Employee.objects.all()
    return render(request,'employees/employee_list.html',{'employees':employees})

def delete_employee(request,employee_id):
    employee=get_object_or_404(Employee,id=employee_id)
    employee.delete()
    return redirect('employee_list')
