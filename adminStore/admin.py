from django.contrib import admin
from .models import Message,Conversation




class MessageAdmin(admin.ModelAdmin):
    list_display = ['id','conversation','sender', 'receiver']


admin.site.register(Message,MessageAdmin)
admin.site.register(Conversation)
