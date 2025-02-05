from django.core.management.base import BaseCommand
from employees.models import Employee
from django.utils import timezone

class Command(BaseCommand):
    help='Process annual leave conversion to bonus'

    def handle(self, *args, **kwargs):
        employees = Employee.objects.filter(is_active=True)
        for employee in employees:
            old_bonus = employee.bonus_amount
            new_bonus = employee.calculate_bonus()
            if new_bonus > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"Procceed bonus for {employee.email}: Added ₹{new_bonus - old_bonus}")
                )
        self.stdout.write(self.style.SUCCESS('Successfully processed all employees'))