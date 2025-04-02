from typing import Dict, Any, List, Union, TypedDict, cast
from openai.types.chat import ChatCompletionMessageParam
from .ai_providers import AIProvider
from ..models import UserProfile, WorkoutPlan, DailyWorkout, Exercise, ExerciseSet
from datetime import datetime, timedelta

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

class DailyWorkoutResponse(TypedDict):
    day: str
    focus: str
    description: str
    duration: str
    intensity: int
    notes: str
    exercises: List[ExerciseData]

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
                    ]
                }}
            ],
            "equipment_needed": ["list", "of", "equipment"],
            "general_guidelines": ["list", "of", "guidelines"]
        }}"""

    def _create_daily_workout_prompt(self, user_profile: UserProfile, day: str) -> str:
        """Create a prompt for generating a daily workout."""
        return f"""Generate a workout for {day} for a user with the following profile:
        Goal: {user_profile.goal}
        Available equipment: {', '.join(user_profile.get_available_equipment_display())}
        
        Please provide a structured JSON response with the following format:
        {{
            "day": "{day}",
            "focus": "Workout focus",
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
            ]
        }}"""

    def _create_exercise(self, exercise_data: ExerciseData) -> Exercise:
        """Create an Exercise instance from exercise data."""
        exercise, created = Exercise.objects.get_or_create(
            name=exercise_data['name'],
            muscle_groups=exercise_data['muscle_groups'],
            defaults={
                'description': exercise_data['description'],
                'equipment_needed': exercise_data['equipment_needed'],
                'difficulty_level': exercise_data['difficulty_level'],
                'instructions': exercise_data['instructions'],
                'tips': exercise_data.get('tips', '')
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
        
        # Create the workout plan
        week_start_date = datetime.now().date()
        workout_plan = WorkoutPlan.objects.create(
            user=user_profile.user,
            week_start_date=week_start_date,
            equipment_needed=response['equipment_needed'],
            general_guidelines=response['general_guidelines']
        )

        # Create daily workouts and their exercises
        for workout_data in response['weekly_plan']:
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

    def generate_daily_workout(self, user_profile: UserProfile, day: str, workout_plan: WorkoutPlan) -> DailyWorkout:
        """Generate a daily workout for a specific day."""
        prompt = self._create_daily_workout_prompt(user_profile, day)
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are a professional personal trainer creating personalized workout plans. You must always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        response = cast(DailyWorkoutResponse, self.ai_provider.generate_completion(messages))
        
        # Create the daily workout
        daily_workout = DailyWorkout.objects.create(
            workout_plan=workout_plan,
            day=response['day'],
            focus=response['focus'],
            description=response['description'],
            duration=response['duration'],
            intensity=response['intensity'],
            notes=response.get('notes', '')
        )

        # Create exercises and their sets
        for exercise_data in response['exercises']:
            exercise = self._create_exercise(exercise_data)
            self._create_exercise_set(exercise, daily_workout, exercise_data)

        return daily_workout 