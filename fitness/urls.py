# fitness/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('workout-plan/', views.WeeklyWorkoutPlanView.as_view(), name='workout_plan'),
    path('workout-plan/<int:pk>/', views.DailyWorkoutView.as_view(), name='daily_workout'),
]
