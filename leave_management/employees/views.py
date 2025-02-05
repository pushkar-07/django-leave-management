import pandas as pd
from django.shortcuts import render,get_object_or_404,redirect
from .models import Employee,LeaveApplication,BonusClaim
from .forms import LeaveApplicationForm,CustomAuthenticationForm,BankDetailsForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

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
def update_bank_details(request):
    try:
        employee= Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request,"Employee profile not found.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = BankDetailsForm(request.POST,instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request,"Bank details updated successfully!")
            return redirect('bonus_dashboard')
    else:
            form = BankDetailsForm(instance=employee)
    return render(request,'employees/update_bank_details.html',{'form':form})

@login_required
def bonus_dashboard(request):
    try:
        employee=Employee.objects.get(email=request.user.email)
        claims = BonusClaim.objects.filter(employee=employee).order_by('-created_at')

        context={
            'employee': employee,
            'claims': claims,
            'has_bank_details': all([
                employee.bank_account_number,
                employee.bank_name,
                employee.ifsc_code
            ])
        }
        return render(request,'employees/bonus_dashboard.html',context)
    except Employee.DoesNotExist:
        messages.error(request,"Employee profile not found.")
        return redirect('dashboard')


@staff_member_required
@require_POST
def calculate_all_bonuses(request):
    employees = Employee.objects.filter(is_active=True)
    processed_count = 0
    
    for employee in employees:
        if employee.leave_balance > 22:
            bonus = employee.calculate_bonus()
            if bonus > 0:
                processed_count += 1
                
    messages.success(request, f"Processed bonus calculation for {processed_count} employees.")
    return redirect('admin_dashboard')

@login_required
def claim_bonus(request):
    if request.method != 'POST':
        messages.error(request,"Invalid request method.")
        return redirect('bonus_dashboard')
    
    try:
        employee = Employee.objects.get(email=request.user.email)
        if not employee.is_active:
            messages.error(request,"You are no longer active in the system.")
            return redirect('bonus_dashboard')
        
        if not all([employee.bank_account_number,
                employee.bank_name,
                employee.ifsc_code]):
            messages.warning(request,"Please update your bank details first.")
            return redirect('update_bank_details')
        
        if employee.bonus_amount <= 0:
            messages.warning(request, "No bonus amount available for claiming.")
            return redirect('bonus_dashboard')

        # Check if there's already a pending claim
        pending_claim = BonusClaim.objects.filter(
            employee=employee,
            status='Pending'
        ).exists()

        if pending_claim:
            messages.warning(request, "You already have a pending bonus claim.")
            return redirect('bonus_dashboard')
        
        claim = BonusClaim.objects.create(
            employee=employee,
            amount=employee.bonus_amount
        )
        messages.success(request, f"Bonus claim of ₹{employee.bonus_amount} submitted successfully!")
        return redirect('bonus_dashboard')
    
    except Employee.DoesNotExist:
        messages.error(request,"Employee profile not found.")
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('bonus_dashboard')


@staff_member_required
def manage_bonus_claims(request):
    claims = BonusClaim.objects.all().order_by('-created_at')
    return render(request,'employees/manage_bonus_claims.html',{'claims':claims})

@staff_member_required
def process_bonus_claim(request,claim_id):
    claim=get_object_or_404(BonusClaim,id=claim_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        transaction_id = request.POST.get('transaction_id')

        if status == 'Paid' and not transaction_id:
            messages.error(request, "Transaction ID is required for paid claims.")
            return render(request, 'employees/process_bonus_claim.html', {'claim': claim})
        claim.status = status
        claim.admin_remarks = remarks
        claim.transaction_id = transaction_id
        claim.processed_at = timezone.now()
        claim.save()

        # Sending email notification
        subject = f"Bonus Claim Status Update: {status}"
        message = f"""
        Dear {claim.employee.first_name},
        
        Your bonus claim of ₹{claim.amount} has been {status.lower()}.
        
        Remarks: {remarks}
        {f'Transaction ID: {transaction_id}' if transaction_id else ''}
        
        Best regards,
        HR Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [claim.employee.email],
            fail_silently=False
        )
        
        messages.success(request, f"Bonus claim {status.lower()} successfully.")
        return redirect('manage_bonus_claims')
        
    return render(request, 'employees/process_bonus_claim.html', {'claim': claim})

@login_required
def withdraw_bonus(request,claim_id):
    try:
        claim = get_object_or_404(BonusClaim,id=claim_id)

        #Verify claim belongs to logged in employee
        if claim.employee.email != request.user.email:
            messages.error(request,"Unauthorized access.")
            return redirect('bonus_dashboard')
        
        #verify claim is in approved statuss
        if claim.status != 'Approved':
            messages.error(request,"Only approved claims can be withdrawn.")
            return redirect('bonus_dashboard')
         # update claim status to paid
        claim.status='Paid'
        claim.processed_at = timezone.now()
        claim.save()

        messages.success(request,"Bonus withdrawn successfully!")

        # sending email
        subject="Bonus Withdrawal Confirmation"
        message= f"""
        Dear {claim.employee.first_name},

        Your bonus withdrawal of Rs.{claim.amount} has been proccessed successfully.

        Best regards,
        HR Team
        """
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [claim.employee.email],
            fail_silently=False
        )
    except Exception as e:
        messages.error(request,f"An error occured: {str(e)}")
    
    return redirect('bonus_dashboard')

