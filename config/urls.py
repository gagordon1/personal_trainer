"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from fitness import views

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('signup')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('fitness/', include('fitness.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='fitness/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='root', http_method_names=['post', 'get']), name='logout'),
]
