from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Shipped_Orders
@receiver(post_save, sender=Shipped_Orders)
def update_order_is_shipped(sender, instance, created, **kwargs):
    if created:
        # Set the is_shipped field of the corresponding Order object to True
        instance.order.is_shipped = True
        instance.order.save()