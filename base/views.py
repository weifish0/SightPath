from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import RoomForm, UserForm, CustomUserCreationForm
import random
from django.http import JsonResponse


from dotenv import load_dotenv
import os
import json
from base.api.persona_chart import persona_chart

import re

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
    context = {
        "page": "login",
        "tpe": "activity"
    }

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
    context = {
        "tpe": "activity",
        "tpe_zh": "活動",
        "form": CustomUserCreationForm(),
        "page": "register"
    }

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
    ourtag = OurTag.objects.all()
    # comp_love = None
    # top3 = None
    # print(user.top3.values())
    # if user.top3 != None:
    #     pk_list = json.loads(user.top3)
    #     preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    #     top3 = OurTag.objects.filter(pk__in=pk_list).order_by(preserved)
    # print(user.love.all())
    return render(request, "base/profile.html",
                  {
                      "user": user,
                      "rooms": rooms,
                      "topics": topics,
                      "ourtag": ourtag
                  })


def chatroom_home(request):
    # topic_category為使用者使用tag搜索時使用， q則為直接使用搜索功能時使用
    topic_category = request.GET.get("topic_category")

    # 搜索查詢的字串
    q = request.GET.get("q")

    # 有topic_category參數則優先使用topic_category進行搜索
    if topic_category != None:
        rooms = Room.objects.filter(Q(topic__name__exact=topic_category))

    # 空的搜索甚麼都不會得到
    elif q == "":
        rooms = Room.objects.none()

    # 使用搜索功能搜索符合條件的 rooms
    elif q != None:
        rooms = Room.objects.filter(Q(topic__name__icontains=q)
                                    | Q(name__icontains=q)
                                    | Q(host__nickname__icontains=q))
    # 預設
    else:
        rooms = Room.objects.all()

    # 以topic索引則找被置頂且符合topic_category的討論串
    if topic_category != None:
        pin_rooms = Room.objects.filter(Q(pin_mode=True)
                                        & Q(topic__name__exact=topic_category))

    # 空的搜索甚麼都不會得到
    elif q == "":
        pin_rooms = Room.objects.none()

    # 使用搜索功能搜索符合條件的 pin_rooms
    elif q != None:
        pin_rooms = Room.objects.filter(Q(pin_mode=True)
                                        & (Q(name__icontains=q) | Q(host__nickname__icontains=q)))
    # 預設
    else:
        pin_rooms = Room.objects.filter(Q(pin_mode=True))

    # 將置頂的討論串從普通rooms中移除
    rooms = rooms.exclude(pin_mode=True).order_by("-updated")

    rooms_count = rooms.count() + pin_rooms.count()
    # 取得所有討論事話題類別
    topics = Topic.objects.all()

    # 排序討論串
    rooms = rooms.order_by("name")
    pin_rooms = pin_rooms.order_by("name")

    context = {
        "rooms": rooms,
        "rooms_count": rooms_count,
        "topics": topics,
        "topic_category": topic_category,
        "pin_rooms": pin_rooms,
        "tpe": "chatroom_home"
    }

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

    if request.user != room.host and not request.user.is_superuser:
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

    if request.user != room.host and not request.user.is_superuser:
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

    if request.user != message.user and not request.user.is_superuser:
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

    if request.user.id != user.id and not request.user.is_superuser:
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
def findpage(request):
    ourtag = OurTag.objects.all()

    # competition_tag為使用者使用tag搜索時使用， q則為直接使用搜索功能時使用
    category = request.GET.get("category")
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    if 'find_competition' in request.build_absolute_uri():
        # 有competition_tag參數則優先使用topic_category進行搜索
        if category != None:
            # TODO: 重複活動出現 需distinct()
            comp_activities = Competition.objects.filter(Q(tags__tag_name__exact=category)
                                                         | Q(our_tags__tag_name__exact=category)).distinct()
        else:
            # TODO: 改進搜索功能
            # TODO: 進階搜索功能
            comp_activities = Competition.objects.filter(Q(name__icontains=q)
                                                         | Q(organizer_title__icontains=q))
        tpe_zh = "比賽"
        tpe = "competition"
    elif 'find_activity' in request.build_absolute_uri():
        if category != None:
            # TODO: 重複活動出現 需distinct()
            comp_activities = Activity.objects.filter(Q(tags__tag_name__exact=category)
                                                      | Q(our_tags__tag_name__exact=category)).distinct()
        else:
            # TODO: 改進搜索功能
            # TODO: 進階搜索功能
            comp_activities = Activity.objects.filter(Q(name__icontains=q))
        tpe_zh = "活動"
        tpe = "activity"

    cnt = comp_activities.count()
    context = {
        "tpe": tpe,
        "tpe_zh": tpe_zh,
        "comp_activities": comp_activities,
        "ourtag": ourtag,
        "count": cnt,
        "category": category,
    }

    lt_ourtag = list(ourtag.values_list('tag_name', flat=True))
    if category in lt_ourtag:
        ind = lt_ourtag.index(category)
        context["comp_activities"] = sorted(
            comp_activities, key=lambda obj: obj.emb[ind], reverse=True)

    return render(request, "base/find_page.html", context)


def info(request, pk):
    if 'competition_info' in request.build_absolute_uri():
        comp_activity = Competition.objects.get(id=pk)
        tpe_zh = "比賽"
        tpe = "competition"
    elif 'activity_info' in request.build_absolute_uri():
        comp_activity = Activity.objects.get(id=pk)
        tpe_zh = "活動"
        tpe = "activity"

    tags = comp_activity.tags.all()
    our_tags = comp_activity.our_tags.all()
    context = {
        "tpe": tpe,
        "tpe_zh": tpe_zh,
        "comp_activity": comp_activity,
        "tags": tags,
        "our_tags": our_tags,
    }
    return render(request, "base/info.html", context)


def about_page(request):
    return render(request, "base/about.html")


# def embvec(request, pk, isourtag):
#     if isourtag == 'comp':
#         obj = Competition.objects.get(id=pk)
#     elif isourtag == 'ourtag':
#         obj = OurTag.objects.get(id=pk)

#     return JsonResponse({"emb": obj.emb, "pk": str(pk), "isourtag": isourtag})


def home_page(request):
    context = card_content(request)
    context["tpe"] = "activity"
    return render(request, "base/home_page.html", context)


def home_update(request):
    offset = int(request.GET.get('offset', 0))
    page_size = 10  # 每次回傳10筆
    all_activities = get_all_activities()  # 這裡換成你的查詢
    activities = all_activities[offset:offset+page_size]
    context = {'comp_activities': activities}
    return render(request, "base/tinder_card.html", context)


CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def cleanhtml(raw_html: str):
    cleantext = re.sub(CLEANR, '', raw_html.strip())
    return cleantext


def card_content(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        user.love_comp
        user.nope_comp
        user.love_activity
        user.nope_activity
    else:
        print("love_act_", request.session.get("love_activity", []))
        request.session.get("nope_comp", [])
        request.session.get("love_activity", [])
        request.session.get("nope_activity", [])

    # competition_tags = CompetitionTag.objects.all()
    competitions = Competition.objects.all()
    activities = Activity.objects.all()

    # filter(Q(name__icontains="") | Q(organizer_title__icontains=""))

    # randomly pick 5 elements
    # valid_id_list = list(competitions.values_list('id', flat=True))
    # random_id_list = random.sample(valid_id_list, min(len(valid_id_list), 5))
    activity_list = list(competitions)
    k = min(3, len(activity_list))
    li = random.sample(activity_list, k)
    for it in li:
        # it.guide_line_html = cleanhtml(it.guide_line_html)
        # it.guide_line_html = it.guide_line_html.replace('\n', '<br>').replace('\r\n', '<br>')
        it.description = it.description.replace("&nbsp;", " ")
    comp_activities = li

    # comp_activities += [x for x in list(activities) if x.pk == 3654]
    activity_list = list(activities)
    k = min(3, len(activity_list))
    li = random.sample(activity_list, k)
    for it in li:
        it.summary = (it.summary or "").replace("&nbsp;", " ")
    comp_activities += li

    # # pick first 8 tags
    # for com in competitions:
    #     id_list = list(com.tags.values_list('id', flat=True))
    #     com.tags.set(com.tags.filter(id__in=id_list[0:8]))
    #     # com.save()
    #     # print(com.tags.all())
    # print(comp_activities)
    count = len(comp_activities)

    return {
        "comp_activities": comp_activities,
        # "competition_tags": competition_tags,
        "count": count
    }


# def rand_content():
#     competition_tags = CompetitionTag.objects.all()
#     competitions = Competition.objects.all()
#     activities = Activity.objects.all()

#     # filter(Q(name__icontains="") | Q(organizer_title__icontains=""))

#     # randomly pick 5 elements
#     # valid_id_list = list(competitions.values_list('id', flat=True))
#     # random_id_list = random.sample(valid_id_list, min(len(valid_id_list), 5))

#     li = random.sample(list(competitions), 3)
#     for it in li:
#         # it.guide_line_html = cleanhtml(it.guide_line_html)
#         # it.guide_line_html = it.guide_line_html.replace('\n', '<br>').replace('\r\n', '<br>')
#         it.guide_line_html = it.guide_line_html.replace("&nbsp;", " ")
#     comp_activities = li

#     # comp_activities += [x for x in list(activities) if x.pk == 3654]
#     li = random.sample(list(activities), 3)
#     for it in li:
#         it.summary = it.summary.replace("&nbsp;", " ")
#     comp_activities += li

#     # # pick first 8 tags
#     # for com in competitions:
#     #     id_list = list(com.tags.values_list('id', flat=True))
#     #     com.tags.set(com.tags.filter(id__in=id_list[0:8]))
#     #     # com.save()
#     #     # print(com.tags.all())
#     # print(comp_activities)
#     count = len(comp_activities)

#     return {"comp_activities": comp_activities,
#             "competition_tags": competition_tags,
#             "count": count}

# 用戶偏好設定


def platform_config(request):
    return render(request, "base/platform_config.html")


@login_required(login_url="login_page")
def persona(request):
    url = ""
    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        sc_arr = json.loads(request.POST.get("scores"))

        user.persona.save("persona" + str(user_id) + ".png",
                          persona_chart(sc_arr))
        user.save()

        url = user.persona.url

    return JsonResponse({
        "url": url
    })


# @login_required(login_url="login_page")
# def save_top3(request):
#     if request.user.is_authenticated:
#         user_id = request.user.id
#         user = User.objects.get(id=user_id)

#         pk_list = json.loads(request.POST.get("sc_sort"))
#         user.top3.set(pk_list)
#         for pos, pk in enumerate(pk_list):
#             user.top3.filter(id=pk).update(ord=pos)

#         user.save()

#     return JsonResponse({})


# @login_required(login_url="login_page")
# def save_model(request):
#     if request.user.is_authenticated:
#         user_id = request.user.id
#         user = User.objects.get(id=user_id)
#         user.artifacts = request.POST.get("artifacts")

#         user.save()

#     return JsonResponse({})


# @login_required(login_url="login_page")
def save_persona(request):
    try:
        love_or_nope = request.POST["love_or_nope"]
        idstr_li = json.loads(request.POST["idstr_li"])
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": repr(e)
        })

    try:
        li = []
        for idstr in idstr_li:
            try:
                head, id = idstr.split("_")
                id = int(id)
                if head == "competition":
                    head = "comp"
                ky = f"{love_or_nope}_{head}"
                li.append((ky, id))
            except:
                continue
        if request.user.is_authenticated:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            for ky, id in li:
                getattr(user, ky).add(id)
            user.save()
        else:
            for ky, id in li:
                if request.session.get(ky) is None:
                    request.session[ky] = [id]
                    request.session.modified = True
                    request.session.save()
                if id not in request.session[ky]:
                    request.session[ky] = [id]
                    request.session.modified = True
                    request.session.save()
                    # history.append("1")
                    # request.session[ky] = history
                    # request.session.save()
            print(ky, request.session[ky])
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": repr(e)
        })

    return JsonResponse({
        "success": True
    })


@login_required(login_url="login_page")
def delete_data(request, pk):
    # 根據網址的用戶名字取得該使用者資料
    user = User.objects.get(id=pk)
    if request.user.id != user.id:
        return redirect("profile", pk=user.id)

    if request.method == "POST":
        user.persona = "loading.gif"

        user.love_comp.clear()
        user.nope_comp.clear()
        user.love_activity.clear()
        user.nope_activity.clear()

        user.top3.clear()
        # user.artifacts = None
        user.save()

        return JsonResponse({
            "success": True
        })

    return JsonResponse({
        "success": False
    })
    # return redirect("profile", pk=user.id)


@login_required(login_url="login_page")
def like_post(request, room_id):
    if request.user.is_authenticated:
        room = get_object_or_404(Room, id=room_id)

        if request.user in room.likes.all():
            room.likes.remove(request.user)
        else:
            room.likes.add(request.user)

        room.save()

        last_url = request.META.get('HTTP_REFERER', None)

        if "topic_category" in last_url:
            topic_category = last_url[last_url.find("?topic_category=") + 16:]
            redirect_url = f"/chatroom_home?topic_category={topic_category}"
        elif "chatroom_home" in last_url:
            redirect_url = "/chatroom_home"
        else:
            redirect_url = f"/room/{room_id}"

        return redirect(redirect_url)

    return redirect('chatroom_home', room_id=room_id)


def line_login_settings(request):
    user = request.user
    try:
        data = user.socialaccount_set.all()[0].extra_data

        # 更改user的資料
        user.line_user_id = data["userId"]
        user.bio = data["statusMessage"]
        user.nickname = data["displayName"]
        user.save()
        '''
        data範例
        {'userId': 'hadifuhasdkfdasffaoifhaof12321', 
        'displayName': '大帥哥', 
        'statusMessage': '向著星辰與大海🐳', 
        'pictureUrl': 'https://profile.line-scdn.net/0hRmvVVACYDUJbLxi11OVzPSt_Dih4XlRQIk5Adj54AXpiSE5EdUgSJDp7AydjTR8dfh5BdmomVHZXPHokRXnxdlwfUHNnHkMXdU5FoA'}
        '''
        return redirect("profile", pk=user.id)
    except:
        return HttpResponse("你不是使用line登入")


def get_all_activities():
    # 依照 id 排序，確保順序穩定且不重複
    competitions = list(Competition.objects.all().order_by('id'))
    activities = list(Activity.objects.all().order_by('id'))
    # 合併後再依 id 排序，確保全局唯一且不重複
    all_objs = competitions + activities
    # 用 id 做唯一性過濾（假設 id 全域唯一，否則可用 (type, id)）
    seen = set()
    unique_objs = []
    for obj in all_objs:
        key = (obj.__class__.__name__, obj.id)
        if key not in seen:
            seen.add(key)
            unique_objs.append(obj)
    return unique_objs
