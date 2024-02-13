from django.contrib import admin
from django.urls import path, include
from . import views
from .views import geofence_check_view, generate_frames
from .views import mark_attendance

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('scanner/', views.scanner, name="scanner"),
    path('geofence/', geofence_check_view, name='geofence_check'),
    path('generate_frames/', generate_frames, name='generate_frames'),
    path('mark_attendance/', mark_attendance, name='mark_attendance'),
]
