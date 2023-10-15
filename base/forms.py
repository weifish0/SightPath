from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User

# 繼承django form的格式，詳細用法參考以下網址
# https://docs.djangoproject.com/en/4.2/topics/forms/
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ["host", "participants"]
        
    
class UserForm(ModelForm):
    class Meta:
        model = User
        # TODO: 更改在 edit_profile中顯示的英文字
        fields = ["nickname", "email","bio"]
        labels = {"nickname": "使用者名稱", "email": "電子信箱", "bio": "個人簡介"}
        
        
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "nickname"]