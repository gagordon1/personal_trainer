# fitness/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import List, Tuple, Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta
from .constants import EQUIPMENT_CHOICES, DIFFICULTY_CHOICES, GOAL_CHOICES

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from django.db.models.query import QuerySet

class Exercise(models.Model):
    """Model for storing reusable exercises."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    muscle_groups = models.JSONField(default=list)  # Add default empty list
    equipment_needed = models.JSONField(default=list)  # Add default empty list
    difficulty_level = models.IntegerField(choices=DIFFICULTY_CHOICES)
    instructions = models.TextField()
    tips = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'muscle_groups']

    def __str__(self) -> str:
        return self.name

    def get_equipment_display(self) -> List[str]:
        """Get human-readable equipment names."""
        if not self.equipment_needed:
            return []
        return [dict(EQUIPMENT_CHOICES).get(equipment, equipment) for equipment in self.equipment_needed]

    def get_available_equipment_choices(self) -> List[str]:
        """Get list of available equipment choices."""
        return [choice[0] for choice in EQUIPMENT_CHOICES]

    def clean(self) -> None:
        """Validate that equipment_needed contains valid choices."""
        if self.equipment_needed:
            valid_equipment = [choice[0] for choice in EQUIPMENT_CHOICES]
            invalid_equipment = [eq for eq in self.equipment_needed if eq not in valid_equipment]
            if invalid_equipment:
                raise ValidationError(f"Invalid equipment choices: {', '.join(invalid_equipment)}")

    def save(self, *args, **kwargs) -> None:
        self.clean()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    if TYPE_CHECKING:
        sets: RelatedManager['ExerciseSet']

class ExerciseSet(models.Model):
    """Model for storing specific sets of an exercise within a workout."""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='sets')
    daily_workout = models.ForeignKey('DailyWorkout', on_delete=models.CASCADE, related_name='exercise_sets')
    sets = models.IntegerField(validators=[MinValueValidator(1)])
    reps = models.CharField(max_length=20)  # Can be "12-15" or "30 seconds" for timed exercises
    rest_time = models.CharField(max_length=20, default='60 seconds')
    weight = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True)  # Optional notes for this specific set
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['exercise']

    def __str__(self) -> str:
        return f"{self.exercise.name} - {self.sets}x{self.reps}"

    def save(self, *args, **kwargs) -> None:
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='general_fitness')
    workouts_per_week = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        default=3
    )
    available_equipment = models.JSONField(default=list)
    fitness_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def get_available_equipment_display(self) -> List[str]:
        if not self.available_equipment:
            return []
        return [dict(EQUIPMENT_CHOICES).get(equipment, equipment) for equipment in self.available_equipment]

    def get_available_equipment_choices(self) -> List[str]:
        return [choice[0] for choice in EQUIPMENT_CHOICES]

    def clean(self) -> None:
        """Validate that available_equipment contains valid choices."""
        if self.available_equipment:
            valid_equipment = [choice[0] for choice in EQUIPMENT_CHOICES]
            invalid_equipment = [eq for eq in self.available_equipment if eq not in valid_equipment]
            if invalid_equipment:
                raise ValidationError(f"Invalid equipment choices: {', '.join(invalid_equipment)}")

    def save(self, *args, **kwargs) -> None:
        self.clean()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    week_start_date = models.DateField(null=True, blank=True)  # Temporarily allow null
    equipment_needed = models.JSONField(default=list)  # Add default empty list
    general_guidelines = models.JSONField(default=dict)  # Add default empty dict
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def get_equipment_display(self) -> List[str]:
        """Get human-readable equipment names."""
        if not self.equipment_needed:
            return []
        return [dict(EQUIPMENT_CHOICES).get(equipment, equipment) for equipment in self.equipment_needed]

    def clean(self) -> None:
        """Validate that equipment_needed contains valid choices."""
        if self.equipment_needed:
            valid_equipment = [choice[0] for choice in EQUIPMENT_CHOICES]
            invalid_equipment = [eq for eq in self.equipment_needed if eq not in valid_equipment]
            if invalid_equipment:
                raise ValidationError(f"Invalid equipment choices: {', '.join(invalid_equipment)}")

    def save(self, *args, **kwargs) -> None:
        self.clean()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user.username} - Week of {self.week_start_date or 'Unspecified'}"

    if TYPE_CHECKING:
        daily_workouts: RelatedManager['DailyWorkout']

class DailyWorkout(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='daily_workouts')
    day = models.CharField(max_length=20, null=True, blank=True)  # Temporarily allow null
    focus = models.CharField(max_length=100, null=True, blank=True)  # Temporarily allow null
    description = models.TextField(null=True, blank=True)  # Temporarily allow null
    duration = models.CharField(max_length=20, null=True, blank=True)  # Temporarily allow null
    intensity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,  # Temporarily allow null
        blank=True  # Temporarily allow null
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['workout_plan', 'day']
        ordering = ['day']

    def __str__(self) -> str:
        return f"{self.workout_plan.user.username} - {self.day or 'Unnamed Day'}"

    def mark_as_sent(self) -> None:
        self.sent = True
        self.sent_at = datetime.now()
        self.save()

    def save(self, *args, **kwargs) -> None:
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    if TYPE_CHECKING:
        exercise_sets: RelatedManager['ExerciseSet']
