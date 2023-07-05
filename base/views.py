from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room,Topic
from .forms import RoomForm

def profile(request):
    return render(request, "base/profile.html")

def chatroom_home(request):
    category = request.GET.get("category") if request.GET.get("category") != None else ""
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    
    if category != "":
        rooms = Room.objects.filter(Q(topic__name__icontains=category))
    else:
        rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(host__username__icontains=q))
    
    rooms_count = rooms.count()
    
    topics = Topic.objects.all()
    context = {"rooms":rooms, "rooms_count":rooms_count, "topics":topics}
    return render(request, "base/chatroom_home.html", context)

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
            return redirect("chatroom_home")   
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
            return redirect("chatroom_home")
    return render(request, "base/room_form.html", context)

def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    context = {"obj": room}
    if request.method == "POST":
        room.delete()
        return redirect("chatroom_home")
    return render(request, "base/delete.html", context)