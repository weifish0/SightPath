from django.forms import ModelForm
from .models import Room

# 繼承django form的格式，詳細用法參考以下網址
# https://docs.djangoproject.com/en/4.2/topics/forms/
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"