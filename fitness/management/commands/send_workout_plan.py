from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any
from fitness.models import WorkoutPlan, DailyWorkout

class Command(BaseCommand):
    help = 'Sends workout plans to users'

    def add_arguments(self, parser):
        parser.add_argument('--weekly', action='store_true', help='Send weekly plans')
        parser.add_argument('--daily', action='store_true', help='Send daily workouts')
        parser.add_argument('--user-id', type=int, help='Specific user ID to send plan to')
        parser.add_argument('--plan-id', type=int, help='Specific workout plan ID to send')

    def handle(self, *args, **options):
        User = get_user_model()
        today = timezone.now().date()
        
        if options['weekly']:
            # Send weekly plans
            plans = WorkoutPlan.objects.filter(week_start_date=today + timedelta(days=1))
            
            if options['user_id']:
                plans = plans.filter(user_id=options['user_id'])
            if options['plan_id']:
                plans = plans.filter(id=options['plan_id'])
            
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
        
        elif options['daily']:
            # Send daily workouts
            daily_workouts = DailyWorkout.objects.filter(
                date=today,
                sent=False
            )
            
            if options['user_id']:
                daily_workouts = daily_workouts.filter(workout_plan__user_id=options['user_id'])
            if options['plan_id']:
                daily_workouts = daily_workouts.filter(workout_plan_id=options['plan_id'])
            
            for daily_workout in daily_workouts:
                try:
                    user = daily_workout.workout_plan.user
                    
                    # Send daily workout email
                    send_mail(
                        subject=f'Your Workout for {today.strftime("%A")}',
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
        
        else:
            self.stdout.write(self.style.ERROR('Please specify either --weekly or --daily'))
