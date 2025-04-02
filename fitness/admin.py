from django.contrib import admin
from .models import UserProfile, WorkoutPlan, DailyWorkout, Exercise, ExerciseSet

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty_level', 'get_muscle_groups', 'get_equipment')
    list_filter = ('difficulty_level',)
    search_fields = ('name', 'description', 'instructions')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_muscle_groups(self, obj):
        return ', '.join(obj.muscle_groups)
    get_muscle_groups.short_description = 'Muscle Groups'
    
    def get_equipment(self, obj):
        return ', '.join(obj.get_equipment_display())
    get_equipment.short_description = 'Equipment'

@admin.register(ExerciseSet)
class ExerciseSetAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'daily_workout', 'sets', 'reps', 'rest_time', 'weight')
    list_filter = ('exercise', 'daily_workout__workout_plan')
    search_fields = ('exercise__name', 'daily_workout__workout_plan__user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'exercise', 
            'daily_workout', 
            'daily_workout__workout_plan',
            'daily_workout__workout_plan__user'
        )

admin.site.register(UserProfile)
admin.site.register(WorkoutPlan)
admin.site.register(DailyWorkout)

# Register your models here.
