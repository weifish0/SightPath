from django.contrib import admin
from .models import Room, Topic, Message, Competition, User, CompetitionTag


# class CompetitionTagAdmin(admin.ModelAdmin):
#     list_display = ("id","tag_name")

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Competition)
admin.site.register(User)
admin.site.register(CompetitionTag)