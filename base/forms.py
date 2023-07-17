from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User

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
        fields = ["username", "email"]