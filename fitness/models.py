# fitness/models.py
from django.db import models
from django.contrib.auth.models import User
from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta

class UserProfile(models.Model):
    GOAL_CHOICES: List[Tuple[str, str]] = [
        ('strength', 'Strength'),
        ('endurance', 'Endurance'),
        ('flexibility', 'Flexibility'),
        ('weight_loss', 'Weight Loss'),
        ('general_fitness', 'General Fitness'),
    ]

    EQUIPMENT_CHOICES: List[Tuple[str, str]] = [
        ('barbell', 'Barbell'),
        ('bench', 'Bench'),
        ('bodyweight', 'Bodyweight Only'),
        ('dumbbells', 'Dumbbells'),
        ('full_gym_access', 'Full Gym Access'),
        ('kettlebells', 'Kettlebells'),
        ('pool', 'Pool'),
        ('pull_up_bar', 'Pull-up Bar'),
        ('resistance_bands', 'Resistance Bands'),
        ('running_trails', 'Running Trails'),
        ('squat_rack', 'Squat Rack'),
        ('yoga_mat', 'Yoga Mat'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    workouts_per_week = models.IntegerField()
    available_equipment = models.JSONField(default=list)

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def get_available_equipment_display(self) -> List[str]:
        if not self.available_equipment:
            return []
        return [dict(self.EQUIPMENT_CHOICES).get(equipment, equipment) for equipment in self.available_equipment]

    def get_available_equipment_choices(self) -> List[str]:
        return [choice[0] for choice in self.EQUIPMENT_CHOICES]

class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    plan_text = models.TextField()

    class Meta:
        unique_together = ['user', 'week_start_date']
        ordering = ['-week_start_date']

    def __str__(self) -> str:
        return f"Weekly plan for {self.user.username} starting {self.week_start_date}"

class DailyWorkout(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    date = models.DateField()
    workout_text = models.TextField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['workout_plan', 'date']
        ordering = ['date']

    def __str__(self) -> str:
        return f"Workout for {self.workout_plan.user.username} on {self.date}"

    def mark_as_sent(self) -> None:
        self.sent = True
        self.sent_at = datetime.now()
        self.save()
