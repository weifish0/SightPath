from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User
from allauth.account.forms import SignupForm
from django import forms

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
        fields = ["nickname", "email", "bio"]
        labels = {"nickname": "暱稱", "email": "電子信箱", "bio": "個人簡介"}
        
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2", "nickname"]
        
# TODO 覆寫 django allauth 預設註冊模板
# class CustomSocialAccountSignupForm(SignupForm):
#     nickname = forms.CharField(max_length=30)
#     def save(self, request):
#         nickname = self.cleaned_data.pop('nickname')
#         email = self.cleaned_data.pop('email')
#         user = super(CustomSocialAccountSignupForm, self).save(request)
#         user.nickname = self.cleaned_data['nickname']
#         user.email = self.cleaned_data['email']
#         user.save()
#         return user