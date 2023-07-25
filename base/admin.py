from django.contrib import admin
from .models import Room, Topic, Message, Competition, User, CompetitionTag


class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username", "email")
    
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("id","name")

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(CompetitionTag)