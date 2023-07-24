from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import Room,Topic, Message, User
from .forms import RoomForm, UserForm, CustomUserCreationForm

"""
目標
1. 爬蟲資料處理
2. Line登入
3. line bot
返回上頁
4. 測試程式
5. class-based views
"""

def home_page(request):
    
    context = {"guide": "<figure class='image'><img src='https://files.bountyhunter.co/contest/public/202303/d6a5595e-3e9c-4d89-9f3a-9063c72f9f6c.jpg'></figure><p>&nbsp;</p>"}
    return render(request, "base/home_page.html", context)


def login_page(request):
    # 假如用戶已經登入了，就把他送回主頁
    if request.user.is_authenticated:
        return redirect("chatroom_home")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # 嘗試在資料庫中搜索 email， 找不到則回傳帳號不存在，
        # 並且將使用者送回登入頁面
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "帳號不存在")
            return render(request, "base/login_register.html")
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("chatroom_home")
        else:
            messages.error(request, "密碼錯誤")
            return render(request, "base/login_register.html")
    
    # context中參數告訴template要註冊頁面還是登入頁面    
    context = {"page": "login"}
    
    return render(request, "base/login_register.html", context)


def register_page(request):
    context = {"form": CustomUserCreationForm()}
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("chatroom_home")
        # TODO: 補充註冊錯誤的原因提示
        else:
            messages.error(request, "格式錯誤")
    
    return render(request, "base/login_register.html", context)


def logout_user(request):
    logout(request)
    
    # TODO: 新增回到上一頁功能，而非主頁
    return redirect("chatroom_home")


def profile(request, pk):
    user = User.objects.get(username=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    context = {"user": user, "rooms": rooms, "topics":topics}
    return render(request, "base/profile.html", context)


def chatroom_home(request):
    # topic_category為使用者使用tag搜索時使用， q則為直接使用搜索功能時使用
    topic_category = request.GET.get("topic_category")
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    
    # 有topic_category參數則優先使用topic_category進行搜索
    if topic_category != None:
        rooms = Room.objects.filter(Q(topic__name__exact=topic_category))
    else:
        rooms = Room.objects.filter(Q(topic__name__icontains=q)
                                    | Q(name__icontains=q)
                                    | Q(host__username__icontains=q))
    
    rooms_count = rooms.count()
    topics = Topic.objects.all()
    
    context = {"rooms":rooms, "rooms_count":rooms_count, 
               "topics":topics, "topic_category": topic_category}
    
    # 當用戶已登入，才會顯示房間通知
    if request.user.is_authenticated:
        user_now = request.user
        
        # 篩選出回覆該使用者貼文的最近15則通知
        myrooms_replies = Message.objects.filter(Q(room__host__username__contains=user_now) 
                                                 & ~Q(user__username=user_now)).order_by("-created")[:15]
        
        context = {"rooms":rooms, "rooms_count":rooms_count, 
                    "topics":topics, "myrooms_replies": myrooms_replies, "topic_category": topic_category}
    
    return render(request, "base/chatroom_home.html", context)


def room(request,pk):
    # 獲取使用者點進的room的詳細資訊
    room = Room.objects.get(id=pk)
    # 讓早發布的訊息在上面，新發布的在下面
    messages = room.message_set.all().order_by("created")
    participants = room.participants.all()
    
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)
    
    context = {"room": room, "room_messages": messages, "participants": participants}
    
    return render(request, "base/room.html", context)


@login_required(login_url="login_page")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    superuser_auth = False
    
    topic_category = request.GET.get("topic_category")
    if topic_category == "None":
        topic_category = ""
    
    # 管理員具有權限可在此新增room tag
    if request.user.is_superuser:
        superuser_auth = True
        
    # 使用者送出表單
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        
        # 超級帳號可以直接以此創建topic
        if superuser_auth:
            topic, created = Topic.objects.get_or_create(name=topic_name)
        else:
            topic = Topic.objects.get(name=topic_name)
        
        # 在資料庫中新增room
        room = Room.objects.create(host=request.user,
                                   topic=topic,
                                   name=request.POST.get("name"),
                                   description=request.POST.get("description"))
        
        return redirect("room", room.id)   
    
    context = {"form": form, "topics": topics, "topic_category": topic_category, "superuser_auth": superuser_auth}   
    return render(request, "base/room_form.html", context)


@login_required(login_url="login_page")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("你沒有權限")
    
    # 抓取該討論室上次在資料庫存的資料
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.method == "POST":
        # 取得使用者輸入或選取的標籤
        topic_name = request.POST.get("topic")
        topic = Topic.objects.get(name=topic_name)
        
        # 更新資料庫的資料
        room.name = request.POST.get("username")
        room.description = request.POST.get("description")
        room.topic = topic
        room.save()
        
        return redirect("room", room.id)
    
    context = {"form": form, "topics": topics, "room": room, "page": "update_room"}    
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


@login_required(login_url="login_page")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse("你沒有權限")
    
    context = {"obj": message}
    
    if request.method == "POST":
        message.delete()
        return redirect("chatroom_home")
    
    return render(request, "base/delete.html", context)


@login_required(login_url="login_page")
def edit_profile(request, pk):
    # 根據網址的用戶名字取得該使用者資料
    user = User.objects.get(username=pk)
    
    if request.user.username != user.username:
        return HttpResponse("你沒有權限")
 
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", pk=user.username)
    
    form = UserForm(instance=user)
    context = {"form": form}
    return render(request, "base/edit_profile.html", context)
    