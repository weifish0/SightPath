from django.shortcuts import render
from django.http import HttpResponse
from .models import Room


def profile(request):
    return render(request, "base/profile.html")

def home(request):
    rooms = Room.objects.all()
    contex = {"rooms":rooms}
    return render(request, "base/home.html", contex)

def room(request,pk):
    rooms = Room.objects.get(id=pk)
    contex = {"rooms": rooms}
    return render(request, "base/room.html", contex)