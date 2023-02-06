from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from userprofile.models import Userprofile

class Command(BaseCommand):
    help = 'Assign edit_product permission to all vendors'

    def handle(self, *args, **kwargs):
        permission = Permission.objects.filter(content_type__app_label='store')
        id_list = [p.id for p in permission]
        
        for profile in Userprofile.objects.filter(is_vendor=True):
           profile.user.user_permissions.add(*id_list)
        # permission = Permission.objects.get_or_create(content_type__app_label='store', codename='change_product')
        # print((permission[0].id))
        
        # for profile in Userprofile.objects.filter(is_vendor=True):
        #    profile.user.user_permissions.add(permission[0].id)