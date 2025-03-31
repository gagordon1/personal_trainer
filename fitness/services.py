# fitness/services.py
import requests
from datetime import datetime, timedelta
from django.conf import settings
from twilio.rest import Client

def get_recovery(access_token):
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    start = f"{yesterday}T00:00:00.000Z"
    end = f"{yesterday}T23:59:59.000Z"
    url = f"https://api.prod.whoop.com/recovery?start={start}&end={end}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[-1]
    return None

def suggest_workout(score, preference):
    level = "light"
    if score >= 80:
        level = "hard"
    elif score >= 50:
        level = "moderate"

    suggestions = {
        "cardio": {
            "hard": "HIIT run, 5x800m intervals",
            "moderate": "30 min steady state jog",
            "light": "20 min walk or light cycling"
        },
        "strength": {
            "hard": "Full body powerlifting circuit",
            "moderate": "Push-pull split workout",
            "light": "Bodyweight resistance routine"
        },
        "mixed": {
            "hard": "CrossFit-style metcon",
            "moderate": "Kettlebell circuit",
            "light": "Yoga and mobility drills"
        }
    }
    return suggestions.get(preference, {}).get(level, "Rest day!")

def send_sms(to, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to
    )
