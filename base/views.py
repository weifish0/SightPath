from django.shortcuts import render
from django.http import HttpResponse
from .models import Room
from .forms import RoomForm

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
    form = RoomForm()
    context = {"form": form}
    return render(request, "base/room_form.html", context)