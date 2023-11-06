from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ("id","nickname", "email")
    
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("id","name","url")

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(CompetitionTag)
admin.site.register(Activity)
admin.site.register(ActivityTag)