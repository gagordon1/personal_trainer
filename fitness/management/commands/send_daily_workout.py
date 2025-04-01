from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from typing import Dict, Any
from fitness.models import DailyWorkout

class Command(BaseCommand):
    help = 'Sends daily workouts to users'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='Specific user ID to send workout to')
        parser.add_argument('--plan-id', type=int, help='Specific workout plan ID to send from')
        parser.add_argument('--date', type=str, help='Specific date to send (YYYY-MM-DD)')

    def handle(self, *args, **options):
        today = timezone.now().date()
        if options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
                return
        else:
            target_date = today

        # Get unsent daily workouts for the target date
        daily_workouts = DailyWorkout.objects.filter(
            date=target_date,
            sent=False
        )
        
        if options['user_id']:
            daily_workouts = daily_workouts.filter(workout_plan__user_id=options['user_id'])
        if options['plan_id']:
            daily_workouts = daily_workouts.filter(workout_plan_id=options['plan_id'])
        
        if not daily_workouts.exists():
            self.stdout.write(self.style.WARNING(f'No unsent workouts found for {target_date}'))
            return
        
        for daily_workout in daily_workouts:
            try:
                user = daily_workout.workout_plan.user
                
                # Send daily workout email
                send_mail(
                    subject=f'Your Workout for {target_date.strftime("%A")}',
                    message=daily_workout.workout_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                # Mark as sent
                daily_workout.mark_as_sent()
                
                self.stdout.write(self.style.SUCCESS(f'Sent daily workout to {user.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send daily workout to {user.email}: {str(e)}'))
