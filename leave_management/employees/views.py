from django.shortcuts import render,get_object_or_404,redirect
from .models import Employee,LeaveApplication
from .forms import LeaveApplicationForm,CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User

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
        if form.is_valid():
            leave=form.save(commit=False)
            leave.employee=request.user
            leave.save()
            return redirect('leave_status')
        else:
            print("Form errors:", form.errors)
        
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
        leave.status=status
        leave.admin_reason=admin_reason
        leave.save()

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
    