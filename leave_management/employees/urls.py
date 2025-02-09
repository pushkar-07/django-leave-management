from django.urls import path
from django.contrib.auth import views as auth_views
from . import views # importing views from the same app
from .views import AdminLoginView,EmployeeLoginView
from django.views.decorators.cache import cache_control
from .forms import CustomPasswordResetForm

urlpatterns = [
    # there is no need for employees to access other employee info
    #path('', views.employee_list, name='employee_list'),
    path('login-admin/',AdminLoginView.as_view(),name='login_admin'),
    path('login-employee/',EmployeeLoginView.as_view(),name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='homepage'), name='logout'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('employee-list/',views.employee_list,name='employee_list'),
    path('password-change/',auth_views.PasswordChangeView.as_view(template_name='employees/password_change.html',success_url='/employees/password-change-done/'),name='password_change'),
    path('password-change-done/',auth_views.PasswordChangeDoneView.as_view(template_name='employees/password_change_done.html'),name='password_change_done'),
    path('password-reset/',auth_views.PasswordResetView.as_view(form_class=CustomPasswordResetForm),name='password_reset'),
    path('delete/<int:employee_id>/',views.delete_employee,name='delete_employee'),
    path('apply-leave/',views.apply_leave,name='apply_leave'),
    path('leave-status/',views.leave_status,name='leave_status'),
    path('manage-leaves/',views.manage_leaves,name='manage_leaves'),
    path('update-leave-status/<int:leave_id>/',views.update_leave_status,name='update_leave_status'),
    path('view-leave/<int:leave_id>/',views.view_leave,name='view_leave'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('employee-section/',views.employee_section,name='employee_section'),
    path('claim-bonus/',views.claim_bonus,name='claim_bonus'),
    path('bonus-dashboard/',views.bonus_dashboard,name='bonus_dashboard'),
    path('update-bank-details/',views.update_bank_details,name='update_bank_details'),
    path('calculate-all-bonuses/',views.calculate_all_bonuses,name='calculate_all_bonuses'),
    path('manage-bonus-claims/',views.manage_bonus_claims,name='manage_bonus_claims'),
    path('process-bonus-claim/<int:claim_id>/',views.process_bonus_claim,name='process_bonus_claim'),
    path('withdraw-bonus/<int:claim_id>/',views.withdraw_bonus,name='withdraw_bonus'),
    path('mark-notification/<int:notification_id>/',views.mark_notifications_as_read,name='mark_notifications_as_read'),
]


    