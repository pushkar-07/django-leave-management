from django.shortcuts import render,get_object_or_404,redirect
from .models import Employee,LeaveApplication
from .forms import LeaveApplicationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView

# Create your views here.


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('manage_leaves')
    return render(request,'employees/dashboard.html')

@staff_member_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request,'employees/employee_list.html',{'employees':employees})

@staff_member_required
def delete_employee(request,employee_id):
    employee=get_object_or_404(Employee,id=employee_id)
    employee.delete()
    return redirect('employee_list')

@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave=form.save(commit=False)
            leave.employee=request.user
            leave.save()
            return redirect('leave_status')
        
    else:
        form = LeaveApplicationForm()
    return render(request,'employees/apply_leave.html',{'form':form})

@login_required
def leave_status(request):
    leave_applications =LeaveApplication.objects.filter(employee=request.user)
    return render(request,'employees/leave_status.html',{'leave_applications': leave_applications})

@staff_member_required
def manage_leaves(request):
    if request.user.is_staff:
        leave_applications = LeaveApplication.objects.all()
        return render(request,'employees/manage_leaves.html',{'leave_applications':leave_applications})
    else:
        return redirect('leave_status')
    
@staff_member_required
def update_leave_status(request,leave_id,status):
    leave=get_object_or_404(LeaveApplication,id=leave_id)
    leave.status=status
    leave.save()
    return redirect('manage_leaves')

class AdminLoginView(LoginView):
    template_name = 'employees/login_admin.html'

class EmployeeLoginView(LoginView):
    template_name='employees/login.html'
