from .models import Order, OrderItem,Discount
from django.db.models import Sum
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from userprofile.api_stripe import get_cupon
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
    
    if instance.order.discount_code and instance.order.is_paid:
        
        cupon,error = get_cupon(instance.order.discount_code) 
        if 'percent_off' in cupon and cupon.get('valid'):
            discount = order_total * ( cupon.get('percent_off') / 100)
            order_total=order_total - discount
    instance.order.paid_amount = order_total 
    instance.order.save()