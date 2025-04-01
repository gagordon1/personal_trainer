# fitness/views.py
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from typing import Any, Dict
from .forms import SignUpForm, EditProfileForm
from .models import UserProfile

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('profile')
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
