"""
URL configuration for moodlist_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from moodlist import views # Add this line
from moodlist.views import UploadPhotoAPIView, GetMoodAPIView, ResetMoodAPIView, IsAuthenticatedAPIView, CallbackAPIView, GetTopTracksAPIView
from django.views.generic import TemplateView
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/upload/', UploadPhotoAPIView.as_view(), name='upload'),
    path('api/get_mood/', GetMoodAPIView.as_view(), name='get_mood'),
    path('api/reset_mood/', ResetMoodAPIView.as_view(), name='reset_mood'),
    path('api/login/', views.login, name='spotify-login'),
    path('api/callback/', CallbackAPIView.as_view(), name='spotify-callback'),
    path('api/is_authenticated/', IsAuthenticatedAPIView.as_view(), name='is-authenticated'),
    path('api/top_tracks/', GetTopTracksAPIView.as_view(), name='get-top-tracks'),
    re_path('.*', TemplateView.as_view(template_name='index.html')),
]
