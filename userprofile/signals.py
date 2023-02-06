from django.contrib.auth.models import User
from .models import customerProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

#from userprofile.api_stripe import vendor_customer

@receiver(post_save,sender=User)
def post_save_user(sender,instance,created,*args, **kwargs):
    if not created:
        try:
            cus= instance.customer            
        except:
            cus = customerProfile.objects.create(user=instance)
            