# fitness/views.py
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login
from typing import Any, Dict
from .forms import SignUpForm, EditProfileForm
from .models import UserProfile, WorkoutPlan, DailyWorkout
from datetime import datetime, timedelta
import logging

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')  # Redirect to login page
    template_name = 'fitness/signup.html'

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        response = super().form_valid(form)
        user = form.save()
        UserProfile.objects.create(
            user=user,
            phone_number=form.cleaned_data['phone_number'],
            goal=form.cleaned_data['goal'],
            workouts_per_week=form.cleaned_data['workouts_per_week'],
            available_equipment=form.cleaned_data['available_equipment']
        )
        # Log the user in
        login(self.request, user)
        return response

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'fitness/profile.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.userprofile #type: ignore
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = EditProfileForm
    template_name = 'fitness/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self) -> UserProfile:
        return self.request.user.userprofile #type: ignore

class WeeklyWorkoutPlanView(LoginRequiredMixin, ListView):
    template_name = 'fitness/weekly_workout_plan.html'
    context_object_name = 'daily_workouts'
    
    def get_queryset(self):
        # Get the most recent workout plan for the user
        workout_plan = WorkoutPlan.objects.filter(
            user=self.request.user
        ).order_by('-week_start_date').first()
        
        if not workout_plan:
            return DailyWorkout.objects.none()
            
        # Get all daily workouts for this plan, ordered by day
        return DailyWorkout.objects.filter(
            workout_plan=workout_plan
        ).prefetch_related(
            'exercise_sets',
            'exercise_sets__exercise'
        ).extra(
            select={'day_order': "CASE day " +
                                "WHEN 'Sunday' THEN 0 " +
                                "WHEN 'Monday' THEN 1 " +
                                "WHEN 'Tuesday' THEN 2 " +
                                "WHEN 'Wednesday' THEN 3 " +
                                "WHEN 'Thursday' THEN 4 " +
                                "WHEN 'Friday' THEN 5 " +
                                "WHEN 'Saturday' THEN 6 " +
                                "END"},
            order_by=['day_order']
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout_plan = WorkoutPlan.objects.filter(
            user=self.request.user
        ).order_by('-week_start_date').first()
        
        if workout_plan:
            context['workout_plan'] = workout_plan
            if workout_plan.week_start_date:
                context['week_start_date'] = workout_plan.week_start_date
                context['week_end_date'] = workout_plan.week_start_date + timedelta(days=6)
            context['equipment_needed'] = workout_plan.get_equipment_display()
            context['general_guidelines'] = workout_plan.general_guidelines
        
        # Only set is_generating to True if we're actually generating a new plan
        context['is_generating'] = self.request.GET.get('generate') == 'true'
        
        return context
        
    def get(self, request, *args, **kwargs):
        # Debug logging
        logger = logging.getLogger(__name__)
        logger.debug(f"GET request received. Generate param: {request.GET.get('generate')}")
        
        # Check if we need to generate a new plan
        if request.GET.get('generate') == 'true':
            try:
                # Call the management command
                from django.core.management import call_command
                logger.debug("Calling generate_workout_plan command")
                call_command('generate_workout_plan', email=request.user.email)
                logger.debug("Command completed successfully")
                
                # Add success message
                from django.contrib import messages
                messages.success(request, 'Workout plan generated successfully!')
                
            except Exception as e:
                # Log the error and set a message for the user
                logger.error(f"Error generating workout plan: {str(e)}")
                from django.contrib import messages
                messages.error(request, f"Error generating workout plan: {str(e)}")
            
            # Redirect to remove the query parameter and force a fresh load
            return HttpResponseRedirect(reverse_lazy('workout_plan'))
            
        return super().get(request, *args, **kwargs)

class DailyWorkoutView(LoginRequiredMixin, DetailView):
    template_name = 'fitness/daily_workout.html'
    context_object_name = 'workout'
    
    def get_queryset(self):
        return DailyWorkout.objects.filter(
            workout_plan__user=self.request.user
        ).prefetch_related(
            'exercise_sets',
            'exercise_sets__exercise'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout = self.get_object()
        context['workout_plan'] = workout.workout_plan
        return context
