from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings

#  用此指令可取得當前資料
# python .\manage.py dumpdata base > data_fixture.json

'''
加載刷新competition_tag和competition資料 (之後部屬可以設置每天早上四點執行一次指令)

# 注意執行順序(由上往下)


# 將比賽fixture讀進資料庫
python3 manage.py loaddata ./base/fixtures/competition_tags_fixture.json
python3 manage.py loaddata ./base/fixtures/competitions_fixture.json


# 將活動fixture讀進資料庫
python3 manage.py loaddata ./base/fixtures/activities_tags_fixture.json
python3 manage.py loaddata ./base/fixtures/activities_fixture.json

# 將18學群tag讀進資料庫
python3 manage.py loaddata ./base/fixtures/ourtag_fixture.json

# 更新比賽fixture
python3 ./base/fixtures/competitions_fixture_generator.py

# 更新活動fixture
python3 ./base/fixtures/activities_fixture_generator.py
'''


class CustomUserManager(BaseUserManager):
    """定義一個沒有username field 的model manager"""

    use_in_migrations = True

    def _create_user(self, email, password, nickname, **extra_fields):
        """透過email和password創建帳號"""
        if not email:
            raise ValueError('The given email must be set')
        if not password:
            raise ValueError('Password is not provided')

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, nickname, **extra_fields):
        """透過密碼創建一個 regular user帳號"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, nickname, **extra_fields)

    def create_superuser(self, email, password, nickname, **extra_fields):
        """透過密碼創建一個 super user帳號"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, nickname, **extra_fields)


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Topic(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class CompetitionTag(models.Model):
    tag_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tag_name}"


class OurTag(models.Model):
    tag_name = models.CharField(max_length=50)
    description = models.CharField(max_length=400)
    emb = models.TextField(null=True)
    emb_org = models.TextField(null=True)

    ord = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.tag_name}"


class Competition(models.Model):
    name = models.TextField()
    url = models.URLField(null=True)
    cover_img_url = models.URLField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    guide_line_html = models.TextField(null=True)
    organizer_title = models.TextField(null=True)
    page_views = models.IntegerField(null=True)
    contact_email = models.EmailField(null=True)
    contact_name = models.TextField(null=True)
    contact_phone = models.TextField(null=True)
    tags = models.ManyToManyField(
        CompetitionTag, blank=True
    )
    limit_highschool = models.BooleanField(null=True)
    limit_none = models.BooleanField(null=True)
    limit_other = models.BooleanField(null=True)

    # 推薦演算法相關
    our_tags = models.ManyToManyField(
        OurTag, blank=True
    )
    emb = models.CharField(max_length=800, null=True)

    def __str__(self):
        return "competition"


class ActivityTag(models.Model):
    tag_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tag_name}"


class Activity(models.Model):
    name = models.TextField()
    eventIdNumber = models.TextField(null=True) # 活動ID
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    eventPlaceType = models.TextField(null=True) # 線上or線下
    location = models.TextField(null=True) # 活動所在縣市
    likeCount = models.IntegerField(null=True)
    page_views = models.IntegerField(null=True)
    isAD = models.BooleanField(null=True)
    cover_img_url = models.URLField(null=True)
    url = models.URLField(null=True) # accupass活動頁面連結
    tags = models.ManyToManyField(
        ActivityTag, blank=True
    )
    guide_line_html = models.TextField(null=True) # 詳細活動內容，會混入HTML標籤
    summary = models.TextField(null=True) # 活動簡介
    precise_location = models.TextField(null=True) # 精確地址(例如: "台北市中山區長安東路一段27號2樓")
    longitude_and_latitude = models.TextField(null=True) # 活動地點經緯度(格式: "經度 緯度")
    add_to_calendar = models.URLField(null=True) # 加入行事曆的網址
    agency_title = models.TextField(null=True) # 活動主辦方


    # 推薦演算法相關
    our_tags = models.ManyToManyField(
        OurTag, blank=True
    )
    emb = models.TextField(null=True)

    def __str__(self):
        return "activity"


class User(AbstractBaseUser, PermissionsMixin):
    bio = models.TextField(null=True, blank=True)
    nickname = models.CharField(max_length=20, null=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(null=True, default="avatar.png")
    line_user_id = models.CharField(max_length=80, null=True, default='', blank=True)
    
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    top3 = models.ManyToManyField(
        OurTag, blank=True, related_name="top3"
    )
    love_comp = models.ManyToManyField(
        Competition, blank=True, related_name="love_comp"
    )
    nope_comp = models.ManyToManyField(
        Competition, blank=True, related_name="nope_comp"
    )
    love_activity = models.ManyToManyField(
        Activity, blank=True, related_name="love_activity"
    )
    nope_activity = models.ManyToManyField(
        Activity, blank=True, related_name="nope_activity"
    )
    persona = models.ImageField(upload_to="persona",
                                height_field=None,
                                width_field=None,
                                max_length=100,
                                default="loading.gif",
                                storage=OverwriteStorage())
    artifacts = models.TextField(null=True, blank=True)

    # 採取 email 作為用戶身分驗證方式
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # 獲取當前模型的最大ID索引值
        max_id = User.objects.aggregate(max_id=models.Max('id'))['max_id']

        if max_id == None:
            max_id = 0

        # 若用戶快捷登陸，則為用戶設置預設用戶名稱
        if self.nickname == None:
            self.nickname = f"第{max_id+1}位使用者"
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Room(models.Model):
    class Meta:
        # 資料庫的索引順序，會優先按照updated排，相同updated則按照created排序，-可以讓該資料變為倒序，也就是最近更新的會在第一個
        ordering = ["-updated", "-created"]

    # 刪除user時不刪除該room, 將值設為 null
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # 刪除topic時不刪除該room, 將值設為 null
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)

    # 討論串名稱
    name = models.CharField(max_length=50)
    # 討論串介紹
    description = models.TextField(null=True, blank=True)

    # 討論串更新時間與建立時間
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # 討論串參與者
    participants = models.ManyToManyField(
        User, related_name="participants", blank=True
    )
    # 置頂貼文
    pin_mode = models.BooleanField(default=False)
    
    #按讚數
    likes = models.ManyToManyField(
        User, related_name="likes", default=0
    )

    def __str__(self):
        return f"{self.name}"


class Message(models.Model):
    # 當使用者被刪除後，刪除他在所有討論室傳的所有訊息
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 當討論室被刪除後，刪除討論室所有的訊息
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.body[0:20]}"