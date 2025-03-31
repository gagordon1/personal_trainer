# fitness/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("whoop/login/", views.whoop_login, name="whoop_login"),
    path("whoop/callback/", views.whoop_callback, name="whoop_callback"),
]
