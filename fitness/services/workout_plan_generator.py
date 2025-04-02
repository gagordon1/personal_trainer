from typing import Dict, Any, List, Union, TypedDict, cast
from openai.types.chat import ChatCompletionMessageParam
from .ai_providers import AIProvider
from ..models import UserProfile, WorkoutPlan, DailyWorkout, Exercise, ExerciseSet
from datetime import datetime, timedelta, date
import json

class ExerciseData(TypedDict):
    name: str
    description: str
    muscle_groups: List[str]
    equipment_needed: List[str]
    difficulty_level: int
    instructions: str
    tips: str
    sets: int
    reps: str
    rest: str
    weight: str
    notes: str

class WorkoutData(TypedDict):
    day: str
    focus: str
    description: str
    duration: str
    intensity: int
    notes: str
    exercises: List[ExerciseData]

class WeeklyPlanResponse(TypedDict):
    weekly_plan: List[WorkoutData]
    equipment_needed: List[str]
    general_guidelines: List[str]

class WorkoutPlanGenerator:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    def _create_weekly_plan_prompt(self, user_profile: UserProfile) -> str:
        """Create a prompt for generating a weekly workout plan."""
        return f"""Generate a weekly workout plan for a user with the following profile:
        Goal: {user_profile.goal}
        Workouts per week: {user_profile.workouts_per_week}
        Available equipment: {', '.join(user_profile.get_available_equipment_display())}
        
        Please provide a structured JSON response with the following format:
        There must be 7 workouts in the weekly plan.
        {{
            "weekly_plan": [
                {{
                    "day": "Monday",
                    "focus": "Upper Body",
                    "description": "Description of the workout",
                    "duration": "45-60 minutes",
                    "intensity": 4,
                    "notes": "Additional notes",
                    "exercises": [
                        {{
                            "name": "Exercise name",
                            "description": "Detailed description of the exercise",
                            "muscle_groups": ["list", "of", "muscle", "groups"],
                            "equipment_needed": ["list", "of", "required", "equipment"],
                            "difficulty_level": 1,
                            "instructions": "Step-by-step instructions",
                            "tips": "Tips for proper form",
                            "sets": 3,
                            "reps": "12-15",
                            "rest": "60 seconds",
                            "weight": "Optional weight",
                            "notes": "Optional notes for this specific set"
                        }}
                        {{
                            "name": "Exercise name",
                            "description": "Detailed description of the exercise",
                            "muscle_groups": ["list", "of", "muscle", "groups"],
                            "equipment_needed": ["list", "of", "required", "equipment"],
                            "difficulty_level": 1,
                            "instructions": "Step-by-step instructions",
                            "tips": "Tips for proper form",
                            "sets": 3,
                            "reps": "12-15",
                            "rest": "60 seconds",
                            "weight": "Optional weight",
                            "notes": "Optional notes for this specific set"
                        }}
                        ...
                    ]
                }}
            ],
            "equipment_needed": ["list", "of", "equipment"],
            "general_guidelines": ["list", "of", "guidelines"]
        }}"""

    def _create_exercise(self, exercise_data: ExerciseData) -> Exercise:
        """Create an Exercise instance from exercise data."""
        # Extract required fields with defaults
        name = exercise_data.get('name', 'Unnamed Exercise')
        description = exercise_data.get('description', '')
        muscle_groups = exercise_data.get('muscle_groups', [])
        equipment_needed = exercise_data.get('equipment_needed', [])
        difficulty_level = exercise_data.get('difficulty_level', 1)
        instructions = exercise_data.get('instructions', '')
        tips = exercise_data.get('tips', '')

        exercise, created = Exercise.objects.get_or_create(
            name=name,
            muscle_groups=muscle_groups,
            defaults={
                'description': description,
                'equipment_needed': equipment_needed,
                'difficulty_level': difficulty_level,
                'instructions': instructions,
                'tips': tips
            }
        )
        return exercise

    def _create_exercise_set(self, exercise: Exercise, daily_workout: DailyWorkout, set_data: ExerciseData) -> ExerciseSet:
        """Create an ExerciseSet instance from set data."""
        return ExerciseSet.objects.create(
            exercise=exercise,
            daily_workout=daily_workout,
            sets=set_data['sets'],
            reps=set_data['reps'],
            rest_time=set_data.get('rest', '60 seconds'),
            weight=set_data.get('weight'),
            notes=set_data.get('notes', '')
        )

    def generate_weekly_plan(self, user_profile: UserProfile) -> WorkoutPlan:
        """Generate a weekly workout plan for a user."""
        prompt = self._create_weekly_plan_prompt(user_profile)
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are a professional personal trainer creating personalized workout plans. You must always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        response = cast(WeeklyPlanResponse, self.ai_provider.generate_completion(messages))
        
        # Calculate the start of the current week (Sunday)
        today = datetime.now().date()
        days_since_sunday = today.weekday() + 1  # +1 because weekday() returns 0-6 (Mon-Sun)
        week_start_date = today - timedelta(days=days_since_sunday)
        week_end_date = week_start_date + timedelta(days=6)
        
        # Delete any existing workout plans for this week
        WorkoutPlan.objects.filter(
            user=user_profile.user,
            week_start_date__gte=week_start_date,
            week_start_date__lte=week_end_date
        ).delete()
        
        # Create the new workout plan
        workout_plan = WorkoutPlan.objects.create(
            user=user_profile.user,
            week_start_date=week_start_date,
            equipment_needed=response.get('equipment_needed', []),
            general_guidelines=response.get('general_guidelines', [])
        )

        # Create daily workouts for the full week
        for workout_data in response.get('weekly_plan', []):
            daily_workout = DailyWorkout.objects.create(
                workout_plan=workout_plan,
                day=workout_data['day'],
                focus=workout_data['focus'],
                description=workout_data['description'],
                duration=workout_data['duration'],
                intensity=workout_data['intensity'],
                notes=workout_data.get('notes', '')
            )

            for exercise_data in workout_data['exercises']:
                exercise = self._create_exercise(exercise_data)
                self._create_exercise_set(exercise, daily_workout, exercise_data)

        return workout_plan

    def _is_remaining_day(self, day: str, today: date, week_end_date: date) -> bool:
        """Check if a given day falls within the remaining days of the week."""
        day_mapping = {
            'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
            'Thursday': 4, 'Friday': 5, 'Saturday': 6
        }
        day_num = day_mapping.get(day)
        if day_num is None:
            return False
            
        # Calculate the date for this day
        days_since_sunday = today.weekday() + 1
        week_start = today - timedelta(days=days_since_sunday)
        day_date = week_start + timedelta(days=day_num)
        
        return today <= day_date <= week_end_date 