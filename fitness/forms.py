from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from typing import Any, Dict
from .models import UserProfile
from .constants import GOAL_CHOICES, EQUIPMENT_CHOICES

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black'})
    )
    goal = forms.ChoiceField(
        choices=GOAL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black'})
    )
    workouts_per_week = forms.IntegerField(
        min_value=1,
        max_value=7,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black'})
    )
    available_equipment = forms.MultipleChoiceField(
        choices=EQUIPMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'rounded border-gray-300 text-black focus:ring-black'}),
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'phone_number', 'goal', 'workouts_per_week', 'available_equipment')

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        # Add styling to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black'
        })

    def clean_email(self) -> str:
        """Check if a user with this email already exists."""
        email = self.cleaned_data.get('email')
        if email is None:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        # Use email as username
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    available_equipment: forms.MultipleChoiceField = forms.MultipleChoiceField(
        choices=EQUIPMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'rounded border-gray-300 text-black focus:ring-black'}),
        required=True
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'goal', 'workouts_per_week', 'available_equipment']

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['available_equipment'] = self.instance.available_equipment or [] 