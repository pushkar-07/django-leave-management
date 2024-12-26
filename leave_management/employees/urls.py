from django.urls import path
from . import views # importing views from the same app

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
]