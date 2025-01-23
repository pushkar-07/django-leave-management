from django.core.management.base import BaseCommand
from employees.models import LeaveApplication
from django.utils.timezone import now
from datetime import timedelta

class Command(BaseCommand):
    help='Automatically approves pending leave applications older than 24 hours'

    def handle(self, *args, **options):
        cutoff_time = now() - timedelta(hours=24)

        pending_leaves=LeaveApplication.objects.filter(status='Pending',applied_date__lte=cutoff_time)

        for leave in pending_leaves:
            leave.status='Approved'
            leave.admin_reason='Automatically Approved after 24 hours of no action.'
            leave.save()
            self.notify_employee(leave)

        self.stdout.write(f"Automatically approved {pending_leaves.count()} leave application(s).")

    def notify_employee(self,leave):
        subject="Your Leave Application Has Been Approved"
        message=f"""
        Dear {leave.employee.first_name},
        
        Your leave application for {leave.leave_date} has been automatically approved as no action was taken by the supervisor within 24 hours.

        Thank you
        """

        try:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [leave.employee.email],
                fail_silently=False,
            )
        except Exception as e:
            self.stderr.write(f"Failed to send email notification:{e}")