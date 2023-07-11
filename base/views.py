from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import Room,Topic
from .forms import RoomForm


def login_page(request):
    # 假如用戶已經登入了，就把他送回主頁
    if request.user.is_authenticated:
        return redirect("chatroom_home")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # 嘗試在資料庫中搜索 username， 找不到則回傳帳號不存在，
        # 並且將使用者送回登入頁面
        try:
            user = User.objects.get(username=email)
        except:
            messages.error(request, "帳號不存在")
            return render(request, "base/login_register.html")
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("chatroom_home")
        else:
            messages.error(request, "密碼錯誤")
            return render(request, "base/login_register.html")
    
    # context中參數傳遞應該render註冊頁面還是登入頁面    
    context = {"page": "login"}
    
    return render(request, "base/login_register.html", context)


def register_page(request):
    context = {"form": UserCreationForm()}
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("chatroom_home")
        else:
            messages.error(request, "格式錯誤")
    
    return render(request, "base/login_register.html", context)


def logout_user(request):
    logout(request)
    return redirect("chatroom_home")


def profile(request):
    return render(request, "base/profile.html")


def chatroom_home(request):
    # category為使用者使用tag搜索時使用， q則為直接使用搜索功能時使用
    category = request.GET.get("category") if request.GET.get("category") != None else ""
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    
    # 有category參數則優先使用category進行搜索
    if category != "":
        rooms = Room.objects.filter(Q(topic__name__icontains=category))
    else:
        rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(host__username__icontains=q))
    
    rooms_count = rooms.count()
    topics = Topic.objects.all()
    
    context = {"rooms":rooms, "rooms_count":rooms_count, "topics":topics}
    
    return render(request, "base/chatroom_home.html", context)


def room(request,pk):
    # 獲取使用者點進的room的詳細資訊
    room = Room.objects.get(id=pk)
    messages = room.message_set.all()
    
    context = {"room": room, "messages": messages}
    
    return render(request, "base/room.html", context)


@login_required(login_url="login_page")
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


@login_required(login_url="login_page")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("你沒有權限")
    
    # 抓取該討論室上次在資料庫存的資料
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


@login_required(login_url="login_page")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("你沒有權限")
    
    context = {"obj": room}
    
    if request.method == "POST":
        room.delete()
        return redirect("chatroom_home")
    
    return render(request, "base/delete.html", context)