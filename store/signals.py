from .models import Order,Shipped_Orders
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def post_save_order(sender, instance,created,*args, **kwargs):    
    try:
        cus=instance.shipping
    except:
        Shipped_Orders.objects.create(order=instance)

