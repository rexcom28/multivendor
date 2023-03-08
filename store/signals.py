from .models import Order, OrderItem,Discount
from django.db.models import Sum
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def post_save_order(sender, instance,created,*args, **kwargs):
    pass
    # try:
    #     cus=instance.shipping
    # except:
    #     Shipped_Orders.objects.create(order=instance)
    

    
         

@receiver(post_save, sender=OrderItem)
def update_order_paided_amount(sender,instance,**kwargs):
    """
    Signal receiver function that updates the paid_amount field of the associated Order object whenever a new
    OrderItem object is saved or updated.
    """
    order_total =0
    for item in instance.order.items.all():
        order_total +=item.price * item.quantity
    
    
    instance.order.paid_amount = order_total
    instance.order.save()