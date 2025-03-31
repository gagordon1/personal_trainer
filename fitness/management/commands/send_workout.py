from django.core.management.base import BaseCommand
from fitness.services import suggest_workout, send_sms

class Command(BaseCommand):
    help = "Send a workout suggestion via SMS"

    def handle(self, *args, **kwargs):
        # Simulate a recovery score
        recovery_score = 75  # change this manually if needed
        preference = "mixed"  # can be 'cardio', 'strength', or 'mixed'
        phone_number = "+16027901721"  # replace with your phone number

        suggestion = suggest_workout(recovery_score, preference)
        message = f"Today’s workout: {suggestion}"
        send_sms(phone_number, message)
        self.stdout.write(self.style.SUCCESS("Workout sent!"))
