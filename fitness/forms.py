from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from typing import Any, Dict
from .models import UserProfile
from .constants import GOAL_CHOICES, EQUIPMENT_CHOICES

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    goal = forms.ChoiceField(choices=GOAL_CHOICES, required=True)
    workouts_per_week = forms.IntegerField(min_value=1, max_value=7, required=True)
    available_equipment = forms.MultipleChoiceField(choices=EQUIPMENT_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'goal', 'workouts_per_week', 'available_equipment')

class EditProfileForm(forms.ModelForm):
    available_equipment: forms.MultipleChoiceField = forms.MultipleChoiceField(
        choices=EQUIPMENT_CHOICES,
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