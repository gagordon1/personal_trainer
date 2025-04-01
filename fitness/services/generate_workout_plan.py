from typing import Dict, Any
from ..models import UserProfile

def generate_workout_plan(user) -> str:
    """
    Generate a personalized weekly workout plan based on user preferences.
    This will be replaced with an AI call in the future.
    """
    profile = user.userprofile
    
    # Get user preferences
    goal = profile.goal
    equipment = profile.available_equipment
    workouts_per_week = profile.workouts_per_week
    
    # Base workout structure
    return f"""Your Weekly Workout Plan

Monday - Upper Body Focus
Warm-up (5 minutes):
- Light jogging or jumping jacks
- Dynamic stretches

Main Workout:
1. Push-ups
   - 3 sets of 10-12 reps
   - Keep back straight, elbows close to body
   - Rest 60 seconds between sets

2. Dumbbell Rows
   - 3 sets of 12-15 reps
   - Keep back straight, pull elbows back
   - Rest 60 seconds between sets

3. Tricep Dips
   - 3 sets of 10-12 reps
   - Keep elbows close to body
   - Rest 60 seconds between sets

Cool-down (5 minutes):
- Light walking
- Static stretches

Wednesday - Lower Body Focus
Warm-up (5 minutes):
- Light jogging or jumping jacks
- Dynamic stretches

Main Workout:
1. Squats
   - 3 sets of 12-15 reps
   - Keep knees aligned with toes
   - Rest 60 seconds between sets

2. Lunges
   - 3 sets of 10 reps per leg
   - Keep front knee aligned with ankle
   - Rest 60 seconds between sets

3. Calf Raises
   - 3 sets of 15-20 reps
   - Full range of motion
   - Rest 60 seconds between sets

Cool-down (5 minutes):
- Light walking
- Static stretches

Friday - Full Body
Warm-up (5 minutes):
- Light jogging or jumping jacks
- Dynamic stretches

Main Workout:
1. Burpees
   - 3 sets of 10 reps
   - Full range of motion
   - Rest 60 seconds between sets

2. Plank
   - 3 sets of 30-45 seconds
   - Keep body straight
   - Rest 60 seconds between sets

3. Mountain Climbers
   - 3 sets of 30 seconds
   - Keep core engaged
   - Rest 60 seconds between sets

Cool-down (5 minutes):
- Light walking
- Static stretches

Saturday - Cardio & Flexibility
Warm-up (5 minutes):
- Light jogging or jumping jacks
- Dynamic stretches

Main Workout:
1. Running or Cycling
   - 20-30 minutes
   - Moderate pace
   - Include intervals if desired

2. Yoga or Stretching
   - 15-20 minutes
   - Focus on major muscle groups
   - Hold stretches 30-45 seconds

Cool-down (5 minutes):
- Light walking
- Static stretches

General Guidelines:
- Stay hydrated throughout the day
- Listen to your body
- Maintain proper form
- Adjust intensity as needed
- Rest days: Tuesday, Thursday, Sunday
- Each workout should take 45-60 minutes

Equipment Needed:
- Bodyweight exercises
- Optional: Dumbbells, resistance bands
- Running shoes for cardio

Remember to:
- Warm up properly before each workout
- Cool down after each session
- Get adequate sleep and nutrition
- Track your progress
- Modify exercises based on your fitness level
"""

def extract_daily_workout(weekly_plan: str, day: str) -> str:
    """Extract the workout for a specific day from the weekly plan."""
    try:
        start = weekly_plan.index(f"{day} -")
        end = weekly_plan.index("\n\n", start)
        return weekly_plan[start:end]
    except ValueError:
        return "Rest Day - Take it easy and focus on recovery!" 