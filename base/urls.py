from django.urls import path
from . import views

urlpatterns = [
    path("profile", views.profile, name="profile"),
    path("room/<str:pk>/", views.room, name="room"),
    path("", views.home, name="home")
]