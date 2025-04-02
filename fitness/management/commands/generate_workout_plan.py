from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from fitness.models import UserProfile, WorkoutPlan, DailyWorkout, Exercise, ExerciseSet
from fitness.services.workout_plan_generator import WorkoutPlanGenerator
from datetime import datetime

class Command(BaseCommand):
    help = 'Generate a weekly workout plan for a specified user'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='ID of the user to generate the workout plan for')

    def handle(self, *args, **options):
        user_id = options['user_id']
        if not user_id:
            raise CommandError('You must provide a user ID using --user-id')
        try:
            user = User.objects.get(pk=user_id)
            user_profile, created = UserProfile.objects.get_or_create(user=user)
        except User.DoesNotExist:
            raise CommandError(f'User with ID {user_id} does not exist')

        generator = WorkoutPlanGenerator()
        weekly_plan = generator.generate_weekly_plan(user_profile)

        # Save the generated plan to the database
        workout_plan = WorkoutPlan.objects.create(
            user=user,
            week_start_date=datetime.now().date(),
            equipment_needed=weekly_plan['equipment_needed'],
            general_guidelines=weekly_plan['general_guidelines']
        )

        # Save daily workouts and their exercises
        for day_info in weekly_plan['weekly_plan']:
            daily_workout = DailyWorkout.objects.create(
                workout_plan=workout_plan,
                day=day_info['day'],
                focus=day_info['focus'],
                description=day_info['description'],
                duration=day_info['duration'],
                intensity=day_info['intensity'],
                notes=day_info.get('notes', '')
            )

            # Create exercises for this daily workout
            for exercise_info in day_info.get('exercises', []):
                # First, get or create the exercise
                exercise, created = Exercise.objects.get_or_create(
                    name=exercise_info['name'],
                    defaults={
                        'description': exercise_info.get('description', ''),
                        'muscle_groups': exercise_info.get('muscle_groups', []),
                        'equipment_needed': exercise_info.get('equipment_needed', []),
                        'difficulty_level': exercise_info.get('difficulty_level', 1),
                        'instructions': exercise_info.get('instructions', ''),
                        'tips': exercise_info.get('tips', '')
                    }
                )

                # Then create the exercise set
                ExerciseSet.objects.create(
                    exercise=exercise,
                    daily_workout=daily_workout,
                    sets=exercise_info['sets'],
                    reps=exercise_info['reps'],
                    rest_time=exercise_info.get('rest', '60 seconds'),
                    weight=exercise_info.get('weight'),
                    notes=exercise_info.get('notes', '')
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully generated workout plan for user {user.username}'))