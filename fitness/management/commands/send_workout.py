from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any
from fitness.models import WorkoutPlan

class Command(BaseCommand):
    help = 'Sends weekly workout plans to users'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='Specific user ID to send plan to')
        parser.add_argument('--plan-id', type=int, help='Specific workout plan ID to send')
        parser.add_argument('--date', type=str, help='Specific week start date (YYYY-MM-DD)')

    def handle(self, *args, **options):
        today = timezone.now().date()
        if options['date']:
            try:
                week_start = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
                return
        else:
            week_start = today + timedelta(days=1)  # Next day

        # Get plans for the target week
        plans = WorkoutPlan.objects.filter(week_start_date=week_start)
        
        if options['user_id']:
            plans = plans.filter(user_id=options['user_id'])
        if options['plan_id']:
            plans = plans.filter(id=options['plan_id'])
        
        if not plans.exists():
            self.stdout.write(self.style.WARNING(f'No plans found for week starting {week_start}'))
            return
        
        for plan in plans:
            try:
                # Send weekly plan email
                send_mail(
                    subject='Your Weekly Workout Plan',
                    message=plan.plan_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[plan.user.email],
                    fail_silently=False,
                )
                
                self.stdout.write(self.style.SUCCESS(f'Sent weekly plan to {plan.user.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send weekly plan to {plan.user.email}: {str(e)}')) 