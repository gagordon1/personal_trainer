from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import Mock, patch
from typing import Any, Dict, List, Optional, cast
from ..models import UserProfile, WorkoutPlan, DailyWorkout, Exercise, ExerciseSet
from ..services.workout_plan_generator import WorkoutPlanGenerator
from ..services.ai_providers import AIProvider
from ..constants import GOAL_CHOICES, EQUIPMENT_CHOICES, DIFFICULTY_CHOICES

class TestWorkoutPlanGenerator(TestCase):
    def setUp(self) -> None:
        # Create test user and profile
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            goal='strength',
            workouts_per_week=3,
            available_equipment=['dumbbells', 'bodyweight'],
            fitness_level=2
        )

        # Create mock AI provider
        self.mock_ai_provider = Mock(spec=AIProvider)
        self.generator = WorkoutPlanGenerator(self.mock_ai_provider)

    def test_generate_weekly_plan(self) -> None:
        # Mock AI response
        mock_response: Dict[str, Any] = {
            "weekly_plan": [
                {
                    "day": "Monday",
                    "focus": "Upper Body",
                    "description": "Upper body strength workout",
                    "duration": "45-60 minutes",
                    "intensity": 4,
                    "notes": "Focus on form",
                    "exercises": [
                        {
                            "name": "Push-ups",
                            "description": "Classic push-up exercise",
                            "muscle_groups": ["chest", "triceps", "shoulders"],
                            "equipment_needed": ["bodyweight"],
                            "difficulty_level": 2,
                            "instructions": "Keep back straight",
                            "tips": "Engage core",
                            "sets": 3,
                            "reps": "12-15",
                            "rest": "60 seconds",
                            "weight": "",
                            "notes": ""
                        }
                    ]
                }
            ],
            "equipment_needed": ["bodyweight"],
            "general_guidelines": ["Stay hydrated", "Warm up properly"]
        }
        self.mock_ai_provider.generate_completion.return_value = mock_response

        # Generate plan
        workout_plan = self.generator.generate_weekly_plan(self.user_profile)

        # Verify WorkoutPlan was created
        self.assertIsInstance(workout_plan, WorkoutPlan)
        self.assertEqual(workout_plan.user, self.user)
        self.assertEqual(workout_plan.equipment_needed, mock_response['equipment_needed'])
        self.assertEqual(workout_plan.general_guidelines, mock_response['general_guidelines'])

        # Verify DailyWorkout was created
        daily_workout = workout_plan.daily_workouts.first()
        self.assertIsNotNone(daily_workout)
        self.assertIsInstance(daily_workout, DailyWorkout)
        daily_workout = cast(DailyWorkout, daily_workout)
        self.assertEqual(daily_workout.day, "Monday")
        self.assertEqual(daily_workout.focus, "Upper Body")
        self.assertEqual(daily_workout.description, "Upper body strength workout")
        self.assertEqual(daily_workout.duration, "45-60 minutes")
        self.assertEqual(daily_workout.intensity, 4)
        self.assertEqual(daily_workout.notes, "Focus on form")

        # Verify Exercise was created
        exercise = Exercise.objects.first()
        self.assertIsNotNone(exercise)
        self.assertIsInstance(exercise, Exercise)
        exercise = cast(Exercise, exercise)
        self.assertEqual(exercise.name, "Push-ups")
        self.assertEqual(exercise.muscle_groups, ["chest", "triceps", "shoulders"])
        self.assertEqual(exercise.equipment_needed, ["bodyweight"])
        self.assertEqual(exercise.difficulty_level, 2)

        # Verify ExerciseSet was created
        exercise_set = daily_workout.exercise_sets.first()
        self.assertIsNotNone(exercise_set)
        self.assertIsInstance(exercise_set, ExerciseSet)
        exercise_set = cast(ExerciseSet, exercise_set)
        self.assertEqual(exercise_set.exercise, exercise)
        self.assertEqual(exercise_set.sets, 3)
        self.assertEqual(exercise_set.reps, "12-15")
        self.assertEqual(exercise_set.rest_time, "60 seconds")

    def test_generate_daily_workout(self) -> None:
        # Create a workout plan first
        workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            week_start_date=timezone.now().date(),
            equipment_needed=["bodyweight"],
            general_guidelines=["Stay hydrated"]
        )

        # Mock AI response
        mock_response: Dict[str, Any] = {
            "day": "Tuesday",
            "focus": "Lower Body",
            "description": "Lower body strength workout",
            "duration": "45-60 minutes",
            "intensity": 4,
            "notes": "Focus on form",
            "exercises": [
                {
                    "name": "Squats",
                    "description": "Bodyweight squats",
                    "muscle_groups": ["quadriceps", "glutes", "hamstrings"],
                    "equipment_needed": ["bodyweight"],
                    "difficulty_level": 2,
                    "instructions": "Keep back straight",
                    "tips": "Engage core",
                    "sets": 3,
                    "reps": "12-15",
                    "rest": "60 seconds",
                    "weight": "",
                    "notes": ""
                }
            ]
        }
        self.mock_ai_provider.generate_completion.return_value = mock_response

        
    def test_exercise_reuse(self) -> None:
        """Test that exercises are reused when they already exist."""
        # Create an existing exercise
        existing_exercise = Exercise.objects.create(
            name="Push-ups",
            description="Classic push-up exercise",
            muscle_groups=["chest", "triceps", "shoulders"],
            equipment_needed=["bodyweight"],
            difficulty_level=2,
            instructions="Keep back straight",
            tips="Engage core"
        )

        # Mock AI response with the same exercise
        mock_response: Dict[str, Any] = {
            "weekly_plan": [
                {
                    "day": "Monday",
                    "focus": "Upper Body",
                    "description": "Upper body strength workout",
                    "duration": "45-60 minutes",
                    "intensity": 4,
                    "notes": "Focus on form",
                    "exercises": [
                        {
                            "name": "Push-ups",
                            "description": "Classic push-up exercise",
                            "muscle_groups": ["chest", "triceps", "shoulders"],
                            "equipment_needed": ["bodyweight"],
                            "difficulty_level": 2,
                            "instructions": "Keep back straight",
                            "tips": "Engage core",
                            "sets": 3,
                            "reps": "12-15",
                            "rest": "60 seconds",
                            "weight": "",
                            "notes": ""
                        }
                    ]
                }
            ],
            "equipment_needed": ["bodyweight"],
            "general_guidelines": ["Stay hydrated"]
        }
        self.mock_ai_provider.generate_completion.return_value = mock_response

        # Generate plan
        workout_plan = self.generator.generate_weekly_plan(self.user_profile)

        # Verify that no new exercise was created
        self.assertEqual(Exercise.objects.count(), 1)
        self.assertEqual(Exercise.objects.first(), existing_exercise)
