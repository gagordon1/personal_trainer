# fitness/models.py
from django.db import models

class UserProfile(models.Model):
    phone_number = models.CharField(max_length=15)
    whoop_user_id = models.CharField(max_length=100, unique=True)
    whoop_access_token = models.TextField()
    workout_preference = models.CharField(max_length=100)  # 'cardio', 'strength', 'mixed'
