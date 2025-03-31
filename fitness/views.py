# fitness/views.py
import requests
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from .models import UserProfile

def whoop_login(request):
    auth_url = (
        "https://api.prod.whoop.com/oauth/oauth2/auth"
        f"?client_id={settings.WHOOP_CLIENT_ID}"
        f"&redirect_uri={settings.WHOOP_REDIRECT_URI}"
        f"&response_type=code&scope=offline+read"
    )
    return redirect(auth_url)

def whoop_callback(request):
    code = request.GET.get("code")
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.WHOOP_REDIRECT_URI,
        "client_id": settings.WHOOP_CLIENT_ID,
        "client_secret": settings.WHOOP_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return HttpResponse("Failed to get tokens", status=400)

    tokens = response.json()
    access_token = tokens["access_token"]

    user_info = requests.get(
        "https://api.prod.whoop.com/oauth/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if user_info.status_code != 200:
        return HttpResponse("Failed to fetch user info", status=400)

    whoop_user_id = user_info.json()["user"]["user_id"]

    profile, _ = UserProfile.objects.get_or_create(
        whoop_user_id=whoop_user_id,
        defaults={"whoop_access_token": access_token, "phone_number": "", "workout_preference": "mixed"}
    )
    profile.whoop_access_token = access_token
    profile.save()

    return HttpResponse("WHOOP account connected successfully!")
