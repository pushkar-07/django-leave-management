from django.urls import path
from django.contrib.auth import views as auth_views
from . import views # importing views from the same app
from .views import AdminLoginView,EmployeeLoginView
urlpatterns = [
    # there is no need for employees to access other employee info
    #path('', views.employee_list, name='employee_list'),
    path('login-admin/',AdminLoginView.as_view(),name='login_admin'),
    path('login-employee/',EmployeeLoginView.as_view(),name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='homepage'), name='logout'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('password-change/',auth_views.PasswordChangeView.as_view(template_name='employees/password_change.html',success_url='/employees/password-change-done/'),name='password_change'),
    path('password-change-done/',auth_views.PasswordChangeDoneView.as_view(template_name='employees/password_change_done.html'),name='password_change_done'),

    path('delete/<int:employee_id>/',views.delete_employee,name='delete_employee'),
    path('apply-leave/',views.apply_leave,name='apply_leave'),
    path('leave-status/',views.leave_status,name='leave_status'),
    path('manage-leaves/',views.manage_leaves,name='manage_leaves'),
    path('update-leave-status/<int:leave_id>/<str:status>/',views.update_leave_status,name='update_leave_status'),
]


    