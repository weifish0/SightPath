from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.CharField(max_length=150, null=True)
    username = models.CharField(max_length=30, null=True)
    email = models.EmailField(unique=True)
    
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
    

class Competition(models.Model):
    name = models.CharField(max_length=100)
    href = models.TextField()
    # competition_img = models.ImageField()
    
    def __str__(self):
        return f"{self.name}"
    