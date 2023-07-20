from django.contrib import admin
from .models import Room, Topic, Message, Competition, User

    
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Competition)
admin.site.register(User)