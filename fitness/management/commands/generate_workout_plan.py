from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from fitness.models import UserProfile, WorkoutPlan
from fitness.services.workout_plan_generator import WorkoutPlanGenerator
from fitness.services.ai_providers import OpenAIProvider
from datetime import datetime, timedelta
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates a workout plan for a specified user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to generate workout plan for')
        parser.add_argument('--days', type=int, default=7, help='Number of days to generate plan for (default: 7)')
        parser.add_argument('--debug', action='store_true', help='Print debug information')

    def handle(self, *args, **options):
        email = options['email']
        days = options['days']
        debug = options['debug']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User with email {email} does not exist'))
            return

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'UserProfile for {email} does not exist'))
            return

        if debug:
            self.stdout.write(self.style.SUCCESS(f'Generating workout plan for {email}'))
            self.stdout.write(f'Profile details:')
            self.stdout.write(f'  Goal: {profile.goal}')
            self.stdout.write(f'  Workouts per week: {profile.workouts_per_week}')
            self.stdout.write(f'  Available equipment: {profile.available_equipment}')
            self.stdout.write(f'  Fitness level: {profile.fitness_level}')

        # Initialize the workout plan generator with OpenAI provider
        ai_provider = OpenAIProvider()
        generator = WorkoutPlanGenerator(ai_provider=ai_provider)

        # Generate the workout plan
        try:
            plan = generator.generate_weekly_plan(user_profile=profile)

            self.stdout.write(self.style.SUCCESS(f'Successfully created workout plan for {email}'))
            self.stdout.write(f'Plan ID: {plan.pk}')
            self.stdout.write(f'Week start date: {plan.week_start_date}')
            self.stdout.write(f'Equipment needed: {", ".join(plan.get_equipment_display())}')

            if debug:
                self.stdout.write(self.style.SUCCESS('Daily workouts:'))
                for workout in plan.daily_workouts.all():
                    self.stdout.write(f'  {workout.day}: {workout.focus}')
                    self.stdout.write(f'    Description: {workout.description}')
                    self.stdout.write(f'    Duration: {workout.duration}')
                    self.stdout.write(f'    Intensity: {workout.intensity}')
                    self.stdout.write('    Exercises:')
                    for exercise_set in workout.exercise_sets.all():
                        self.stdout.write(f'      - {exercise_set.exercise.name}: {exercise_set.sets}x{exercise_set.reps}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error generating workout plan: {str(e)}'))
            if debug:
                import traceback
                self.stderr.write(traceback.format_exc())
