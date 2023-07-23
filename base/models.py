from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.CharField(max_length=150, null=True)
    username = models.CharField(max_length=30, null=True)
    email = models.EmailField(unique=True, null=True)
    
    avatar = models.ImageField(null=True, default="avatar.png")
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    

class Topic(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"


class Room(models.Model):
    class Meta:
        # 資料庫的索引順序，會優先按照updated排，相同updated則按照created排序，-可以讓該資料變為倒序，也就是最近更新的會在第一個
        ordering = ["-updated", "-created"]
    # 刪除使用者時不刪除該房間, 將值設為 null
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # 刪除話題時不刪除該房間, 將值設為 null
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(
        User, related_name="participants", blank=True
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
    
    
class CompetitionTag(models.Model):
    tag_name = models.CharField(max_length=50)
        
    def __str__(self):
        return f"{self.name}"


class Competition(models.Model):
    name = models.TextField()
    url = models.URLField(null=True)
    
    limit_highschool = models.BooleanField(null=True)
    limit_none = models.BooleanField(null=True)
    limit_other = models.BooleanField(null=True)
    
    agency_title = models.TextField(null=True)
    
    page_views = models.IntegerField(null=True)
    
    contact_email = models.TextField(null=True)
    contact_name = models.TextField(null=True)
    contact_phone = models.TextField(null=True)
    
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    
    cover_img_url = models.TextField(blank=True)
    
    tags = models.ManyToManyField(
        CompetitionTag, blank=True
    )
    
    def __str__(self):
        return f"{self.name}"
    