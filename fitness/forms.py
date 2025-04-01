from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from typing import Any, Dict
from .models import UserProfile

class SignUpForm(UserCreationForm):
    email: forms.EmailField = forms.EmailField(required=True)
    phone_number: forms.CharField = forms.CharField(required=True)
    goal: forms.ChoiceField = forms.ChoiceField(choices=UserProfile.GOAL_CHOICES, required=True)
    workouts_per_week: forms.IntegerField = forms.IntegerField(required=True)
    available_equipment: forms.MultipleChoiceField = forms.MultipleChoiceField(
        choices=UserProfile.EQUIPMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'password1', 'password2', 'goal', 'workouts_per_week', 'available_equipment')

class EditProfileForm(forms.ModelForm):
    available_equipment: forms.MultipleChoiceField = forms.MultipleChoiceField(
        choices=UserProfile.EQUIPMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'goal', 'workouts_per_week', 'available_equipment']

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['available_equipment'] = self.instance.available_equipment or [] 