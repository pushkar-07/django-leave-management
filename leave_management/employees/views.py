from django.shortcuts import render,get_object_or_404,redirect
from .models import Employee,LeaveApplication,BonusClaim
from .forms import LeaveApplicationForm,CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

@staff_member_required
def admin_dashboard(request):
    context={
    'total_requests':LeaveApplication.objects.count(),
    'pending_requests': LeaveApplication.objects.filter(status='Pending').count(),
    'approved_requests': LeaveApplication.objects.filter(status='Approved').count(),
    'rejected_requests': LeaveApplication.objects.filter(status='Rejected').count(),
    'total_employees':Employee.objects.filter(is_active=True).count(),
    }
    return render(request,'employees/admin_dashboard.html',context)

@staff_member_required
def employee_section(request):
    context={'total_employees':Employee.objects.filter(is_active=True).count(),}
    return render(request,'employees/employee_section.html',context)

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return render(request,'employees/dashboard.html')

@staff_member_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request,'employees/employee_list.html',{'employees':employees})

@staff_member_required
def delete_employee(request,employee_id):
    employee=get_object_or_404(Employee,id=employee_id)
    employee.is_active=False
    employee.save()
    
    try:
        user=User.objects.get(email=employee.email)
        user.is_active=False
        user.save()
    except User.DoesNotExist:
        pass
    return redirect('employee_list')

@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        try:
            employee=Employee.objects.get(email=request.user.email)
            if form.is_valid():
                leave=form.save(commit=False)
                leave.employee=request.user
                leave.employee_email = request.user.email
                # employee=Employee.objects.filter(email=request.user.email).first()
                if employee.leave_balance > 0:
                    leave.save() #deducting the leave in the model's save method
                    return redirect('leave_status')
                else:
                    form.add_error(None,"Insufficient leave balance.") 
        except Employee.DoesNotExist:
            form.add_error(None, "No employee record found for this user.")   
    else:
        form = LeaveApplicationForm()
    return render(request,'employees/apply_leave.html',{'form':form})
    # if request.method == 'POST':
    #     form = LeaveApplicationForm(request.POST)
    #     employee =Employee.objects.filter(email=request.user.email).first()

    #     if employee and employee.leave_balance <= 0:
    #         messages.error(request,"Insufficient leave balance. cannot apply for leave.")
    #         return render(request,'employees/apply_leave.html',{'form':form})
        
    #     if form.is_valid():
    #         leave = form.save(commit=False)
    #         leave.employee =request.user
    #         leave.employee_email = request.user.email
    #         leave.save()
    #         return redirect('leave_status')
    # else:
    #     form =LeaveApplicationForm()
    # return render(request,'employees/apply_leave.html',{'form':form})

@login_required
def leave_status(request):
    leave_applications =LeaveApplication.objects.filter(employee=request.user)
    return render(request,'employees/leave_status.html',{'leave_applications': leave_applications})

@staff_member_required
def manage_leaves(request):
    if request.user.is_staff:
        leaves = LeaveApplication.objects.all()


        #Filter by employee name:
        employee_name=request.GET.get('employee_name','').strip()
        if employee_name:
            leaves=leaves.filter(Q(employee__first_name__icontains=employee_name)|Q(employee__last_name__icontains=employee_name))

        #Filtering by status:
        status=request.GET.get('status','')
        if status:
            leaves=leaves.filter(status=status)
        
        #Filter by leave type:
        leave_duration=request.GET.get('leave_duration','')
        if leave_duration:
            leaves=leaves.filter(leave_duration=leave_duration)
        
        #sorting by date applied(default):
        sort_by=request.GET.get('sort_by','applied_date')
        leaves=leaves.order_by(sort_by)

        return render(request,'employees/manage_leaves.html',
                      {
                          'leave_applications':leaves,
                          'filters':{
                              'employee_name':employee_name,
                              'leave_duration':leave_duration,
                              'status':status,
                              'sort_by':sort_by,
                          }
                        
                      })
    else:
        return redirect('leave_status')
    
@staff_member_required
def update_leave_status(request,leave_id):
    leave=LeaveApplication.objects.get(id=leave_id)
    if request.method=='POST':
        admin_reason=request.POST.get('admin_reason')
        status=request.POST.get('status')
        previous_status = leave.status
        leave.status=status
        leave.admin_reason=admin_reason
        leave.save()

        if previous_status != status:
            employee=Employee.objects.filter(email=leave.employee.email).first()
            if employee:
                if status == 'Rejected':
                    employee.leave_balance += 1
                    employee.save()
                elif status == 'Approved':
                    pass # leave already deducted during application , no need to deduct again

#sending email
        subject=f"Your Leave Application Status: {status}"
        message=f"""
        Dear {leave.employee.first_name},

        Your leave application for {leave.leave_date} has been {status.lower()}
        Reason: {admin_reason}
        
        Thank you"""
    
        send_mail(subject,message,settings.EMAIL_HOST_USER,[leave.employee.email],fail_silently=False)

        return redirect('manage_leaves')
    return render(request,'employees/update_leave_status.html',{'leave':leave})

@staff_member_required
def view_leave(request,leave_id):
    leave=LeaveApplication.objects.get(id=leave_id)
    return render(request,'employees/view_leave.html',{'leave':leave})

class AdminLoginView(LoginView):
    template_name = 'employees/login_admin.html'
    authentication_form = CustomAuthenticationForm


    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('homepage')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        remember_me=form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(60*60*24*30) #keeping it 30 days
        else:
            self.request.session.set_expiry(0)

        return super().form_valid(form)
    

class EmployeeLoginView(LoginView):
    template_name='employees/login.html'
    authentication_form=CustomAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('homepage')
        return super().dispatch(request, *args, **kwargs)
   
    def form_valid(self, form):
        user=form.get_user()
        if not user.is_active:
            form.add_error(None,"You are no longer an employee of our company.")
            return self.form_invalid(form)
        
        try:
            employee=Employee.objects.get(email=user.email)
            if not employee.is_active:
                form.add_error(None,"You are no longer a part of our company.")
                return self.form_invalid(form)
        except Employee.DoesNotExist:
            form.add_error(None,"No associated employee record found.")
            return self.form_invalid(form)
        
        remember_me=form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(60*60*24*30) #keeping it 30 days
        else:
            self.request.session.set_expiry(0)
        return super().form_valid(form)

@login_required
def claim_bonus(request):
    employee = request.user.employee
    if employee.bonus_amount > 0:
        claim=BonusClaim.objects.create(employee=employee,amount=employee.bonus_amount)
        employee.bonus_amount = 0
        employee.save()
        return redirect('bonus_success')
    return render(request,'employees/no_bonus.html')  