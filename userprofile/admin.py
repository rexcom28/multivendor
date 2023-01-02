from django.contrib import admin
from .models import Userprofile,customerProfile


class customerProfileAdmin(admin.ModelAdmin):
    list_display = ['id','user','stripe_cus_id']

admin.site.register(Userprofile)
admin.site.register(customerProfile,customerProfileAdmin)


