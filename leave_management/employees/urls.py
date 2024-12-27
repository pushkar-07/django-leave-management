from django.urls import path
from . import views # importing views from the same app

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('delete/<int:employee_id>/',views.delete_employee,name='delete_employee'),
]