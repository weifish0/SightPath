from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import *
from .forms import RoomForm, UserForm, CustomUserCreationForm
import random
from django.http import JsonResponse

from dotenv import load_dotenv
import os
import json
from base.api.persona_chart import persona_chart

"""
目標
1. 競賽資料爬蟲資料處理 ok
2. Line登入
3. line bot
4. 返回上頁，自動導向
5. class based views
"""


def login_page(request):
    # 假如用戶已經登入了，就把他送回主頁
    if request.user.is_authenticated:
        return redirect("chatroom_home")

    # context中參數告訴template要渲染登入頁面
    context = {"page": "login"}

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        load_dotenv()
        if password == os.getenv('superuser_key'):
            try:
                superuser_count = User.objects.filter(
                    is_superuser=True).count()
                superuser = User.objects.create_superuser(

                    email=email,
                    password=password,
                    nickname=f'測試帳號{superuser_count}'
                )
                print("成功創建超級帳號")
                login(request, superuser)
                return redirect("chatroom_home")
            except:
                superuser = authenticate(
                    request, email=email, password=password)
                login(request, superuser)
                print("超級帳號登陸")
                return redirect("chatroom_home")

        # 嘗試在資料庫中搜索 email， 找不到則回傳帳號不存在，
        # 並且將使用者送回登入頁面
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "帳號不存在")
            return render(request, "base/login_register.html", context)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("chatroom_home")
        else:
            messages.error(request, "密碼錯誤")
            return render(request, "base/login_register.html", context)

    return render(request, "base/login_register.html", context)


def register_page(request):
    context = {"form": CustomUserCreationForm(), "page": "register"}

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("chatroom_home")
        # TODO: 補充註冊錯誤的原因提示

        else:
            error_message = form.errors.as_text()
            messages.error(request, f"{error_message}")

    return render(request, "base/login_register.html", context)


def logout_user(request):
    logout(request)

    # TODO: 新增回到上一頁功能，而非主頁
    return redirect("chatroom_home")


def profile(request, pk):
    # 根據網址附帶的 user_id 查找使用者
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()

    if user.love != None:
        comp_love = Competition.objects.filter(id__in=json.loads(user.love))
    else:
        comp_love = None

    return render(request, "base/profile.html",
                  {"user": user,
                   "rooms": rooms,
                   "topics": topics,
                   "comp_love": comp_love})


def chatroom_home(request):
    # topic_category為使用者使用tag搜索時使用， q則為直接使用搜索功能時使用
    topic_category = request.GET.get("topic_category")

    # q值若找不到則設為空字串，原本會回傳None，但用django Q物件以None搜索會回報錯誤
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    # 有topic_category參數則優先使用topic_category進行搜索
    if topic_category != None:
        rooms = Room.objects.filter(Q(topic__name__exact=topic_category))
    # 使用搜索功能搜索
    else:
        rooms = Room.objects.filter(Q(topic__name__icontains=q)
                                    | Q(name__icontains=q)
                                    | Q(host__nickname__icontains=q))

    # 找到被置頂的討論串
    pin_rooms = Room.objects.filter(Q(pin_mode=True))
    # 將置頂的討論串從普通rooms中移除
    rooms = rooms.exclude(pin_mode=True).order_by("-updated")

    rooms_count = rooms.count() + pin_rooms.count()
    # 取得所有討論事話題類別
    topics = Topic.objects.all()

    context = {"rooms": rooms, "rooms_count": rooms_count,
               "topics": topics, "topic_category": topic_category,
               "pin_rooms": pin_rooms}

    # TODO: 將其改成用彈出視窗顯示
    # 當用戶已登入，才會顯示房間通知
    if request.user.is_authenticated:
        user_now = request.user.id

        # 篩選出回覆該使用者貼文的最近15則通知
        myrooms_replies = Message.objects.filter(Q(room__host__id__contains=user_now)
                                                 & ~Q(user__id=user_now)).order_by("-created")[:15]

        context.setdefault("myrooms_replies", myrooms_replies)

    return render(request, "base/chatroom_home.html", context)


def room(request, pk):
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

    context = {"room": room, "room_messages": messages,
               "participants": participants}

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

        if topic_name != None and topic_name != "":
            # topice_name不能含有空格
            topic_name = topic_name.replace(" ", "")

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

        room.participants.add(request.user)

        return redirect("room", room.id)

    context = {"form": form, "topics": topics,
               "topic_category": topic_category, "superuser_auth": superuser_auth}
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
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.topic = topic
        room.save()

        return redirect("room", room.id)

    context = {"form": form, "topics": topics,
               "room": room, "page": "update_room"}
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
def pin_room(request, pk):

    if not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    # 將討論室設為置頂
    room = Room.objects.get(id=pk)
    room.pin_mode = True
    room.save()
    return redirect('chatroom_home')


@login_required(login_url="login_page")
def unpin_room(request, pk):

    if not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    # 將討論室取消置頂
    room = Room.objects.get(id=pk)
    room.pin_mode = False
    room.save()
    return redirect('chatroom_home')


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
    user = User.objects.get(id=pk)

    if request.user.id != user.id:
        return HttpResponse("你沒有權限")

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", pk=user.id)

    form = UserForm(instance=user)
    context = {"form": form}
    return render(request, "base/edit_profile.html", context)


# need to sync with def home_page
def find_competitions(request):
    competition_tags = OurTag.objects.all()

    # competition_tag為使用者使用tag搜索時使用， q則為直接使用搜索功能時使用
    competition_category = request.GET.get("competition_category")
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    # 有competition_tag參數則優先使用topic_category進行搜索
    if competition_category != None:
        # TODO: 重複活動出現 需distinct()
        competitions = Competition.objects.filter(Q(tags__tag_name__exact=competition_category)
                                                  | Q(our_tags__tag_name__exact=competition_category)).distinct()
    else:
        # TODO: 改進搜索功能
        # TODO: 進階搜索功能
        competitions = Competition.objects.filter(Q(name__icontains=q)
                                                  | Q(organizer_title__icontains=q))

    competitions_count = competitions.count()

    context = {"competitions": competitions, "competition_tags": competition_tags,
               "competitions_count": competitions_count, "competition_category": competition_category}
    return render(request, "base/find_competitions_page.html", context)
#####


def competition_info(request, pk):
    competition = Competition.objects.get(id=pk)
    tags = competition.tags.all()
    our_tags = competition.our_tags.all()
    context = {"competition": competition, "tags": tags, "our_tags": our_tags}
    return render(request, "base/competition_info.html", context)


def about(request):
    return render(request, "base/about.html")


def embvec(request, pk, isourtag):
    if isourtag == 'comp':
        obj = Competition.objects.get(id=pk)
    elif isourtag == 'ourtag':
        obj = OurTag.objects.get(id=pk)

    return JsonResponse({"emb": obj.emb, "pk": str(pk), "isourtag": isourtag})


def home_page(request):
    return render(request, "base/home_page.html", rand_context())


def home_update(request):
    return render(request, "base/tinder_card.html", rand_context())


def rand_context():
    competition_tags = CompetitionTag.objects.all()
    competitions = Competition.objects.filter(Q(name__icontains="")
                                              | Q(organizer_title__icontains=""))

    # randomly pick 5 elements
    valid_id_list = list(competitions.values_list('id', flat=True))
    random_id_list = random.sample(valid_id_list, min(len(valid_id_list), 5))
    competitions = competitions.filter(id__in=random_id_list)

    # pick first 8 tags
    for com in competitions:
        id_list = list(com.tags.values_list('id', flat=True))
        com.tags.set(com.tags.filter(id__in=id_list[0:8]))
        # com.save()
        # print(com.tags.all())

    competitions_count = competitions.count()

    return {"competitions": competitions,
            "competition_tags": competition_tags,
            "competitions_count": competitions_count}

  # 用戶偏好設定


def platform_config(request):
    return render(request, "base/platform_config.html")


def persona(request):
    url = ""
    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        sc_arr = json.loads(request.GET.get("scores"))

        user.persona.save("persona"+str(user_id)+".png",
                          persona_chart(sc_arr))
        user.save()

        url = user.persona.url

    return JsonResponse({"url": url})


def save(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        # print (request.POST.get("love_or_nope"))
        love_or_nope = request.POST.get("love_or_nope")
        id = int(request.POST.get("id"))
        arr = []

        if love_or_nope == "love":
            if user.love != None:
                arr = json.loads(user.love)
            arr.append(id)
            user.love = json.dumps(arr)
        elif love_or_nope == "nope":
            if user.nope != None:
                arr = json.loads(user.nope)
            arr.append(id)
            user.nope = json.dumps(arr)

        user.save()

    return JsonResponse({})


@login_required(login_url="login_page")
def delete_data(request, pk):
    # 根據網址的用戶名字取得該使用者資料
    user = User.objects.get(id=pk)

    if request.user.id != user.id:
        return redirect("profile", pk=user.id)
    
    user.persona = "loading.gif"
    user.love = None
    user.nope = None
    user.save()
    
    return redirect("profile", pk=user.id)