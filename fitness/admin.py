from django.contrib import admin
from .models import UserProfile, WorkoutPlan, DailyWorkout

admin.site.register(UserProfile)
admin.site.register(WorkoutPlan)
admin.site.register(DailyWorkout)

# Register your models here.
