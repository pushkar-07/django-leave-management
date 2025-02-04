from django.core.management.base import BaseCommand
from employees.models import Employee

class Command(BaseCommand):
    help = 'Credit 2 leaves to all employees'

    def handle(self, *args, **options):
        employees=Employee.objects.all()
        for employee in employees:
            employee.leave_balance += 2

            if employee.leave_balance > 16:
                extra_leaves = employee.leave_balance - 16
                employee.bonus_amount += extra_leaves * 500
                employee.leave_balance = 16

            employee.save()
        self.stdout.write(self.style.SUCCESS("Successfully credited 2 leaves to all employees!"))