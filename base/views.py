from django.shortcuts import render
from django.http import HttpResponse
from .models import Room


def profile(request):
    return render(request, "base/profile.html")

def home(request):
    rooms = Room.objects.all()
    context = {"rooms":rooms}
    return render(request, "base/home.html", context)

def room(request,pk):
    rooms = Room.objects.get(id=pk)
    context = {"rooms": rooms}
    return render(request, "base/room.html", context)

def create_room(request):
    context = {}
    return render(request, "base/room_form.html")