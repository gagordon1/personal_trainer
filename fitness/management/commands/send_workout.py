from django.core.management.base import BaseCommand
from fitness.services import send_workout_suggestion
from django.conf import settings

class Command(BaseCommand):
    help = "Send a workout suggestion via email"

    def handle(self, *args, **kwargs):
        # Debug: Print email settings
        self.stdout.write("Email Settings:")
        self.stdout.write(f"Host: {settings.EMAIL_HOST}")
        self.stdout.write(f"Port: {settings.EMAIL_PORT}")
        self.stdout.write(f"Use TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"User: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"From: {settings.DEFAULT_FROM_EMAIL}")
        
        # Simulate a recovery score
        recovery_score = 75  # change this manually if needed
        preference = "mixed"  # can be 'cardio', 'strength', or 'mixed'
        email = "ggordongpt99@gmail.com"  # using the same email as sender for testing

        send_workout_suggestion(email, recovery_score, preference)
        self.stdout.write(self.style.SUCCESS("Workout suggestion sent via email!"))
