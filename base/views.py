from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room
from .forms import RoomForm

def profile(request):
    return render(request, "base/profile.html")

def home(request):
    # 獲取討論室資料庫的所有資料
    rooms = Room.objects.all()
    context = {"rooms":rooms}
    return render(request, "base/home.html", context)

def room(request,pk):
    # 獲取特定id的討論室
    room = Room.objects.get(id=pk)
    context = {"rooms": room}
    return render(request, "base/room.html", context)

def create_room(request):
    form = RoomForm()
    context = {"form": form}
    # 使用者送出表單
    if request.method == "POST":
        # 在資料庫中新增資料
        form = RoomForm(request.POST)
        if form.is_valid():
            # 符合格式就保存到資料庫，並且回到主頁
            form.save()
            return redirect("home")   
    return render(request, "base/room_form.html", context)

def update_room(request, pk):
    room = Room.objects.get(id=pk)
    # 讓討論室抓取該討論室上次在資料庫存的資料
    form = RoomForm(instance=room)
    context = {"form": form}
    if request.method == "POST":
        # 更新資料庫的資料
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            # 符合格式就保存到資料庫，並且回到主頁
            form.save()
            return redirect("home")
    return render(request, "base/room_form.html", context)

def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    context = {"obj": room}
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", context)