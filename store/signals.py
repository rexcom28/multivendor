from .models import Order, OrderItem,Discount
from django.db.models import Sum
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from userprofile.api_stripe import get_cupon
from adminStore.models import Message,Conversation
from django.utils import timezone


@receiver(post_save, sender=Order)
def post_save_order(sender, instance,created,*args, **kwargs):
    if instance.is_paid :
        conversation,created_conv = Conversation.objects.get_or_create(order=instance)
        # Create messages for each item in the order
        if created_conv:
            for item in instance.items.all():
                seller = item.product.user
                product_name = item.product.title
                quantity = item.quantity
                content = f"You have a new order for {quantity} units of {product_name}."
                Message.objects.create(
                    conversation=conversation,
                    sender=instance.created_by,
                    receiver=seller,
                    content=content,
                    created_at=timezone.now()
                )
            
            #add members to the conversation    
            members = list(instance.items.values_list('product__user', flat=True))
            members.append(instance.created_by)
            conversation.members.set(members)

         

@receiver(post_save, sender=OrderItem)
def update_order_paided_amount(sender,instance,**kwargs):
    """
    Signal receiver function that updates the paid_amount field of the associated Order object whenever a new
    OrderItem object is saved or updated.
    """
    order_total =0
    

    for item in instance.order.items.all():
        order_total +=item.product.price * item.quantity
        
    if instance.order.discount_code and instance.order.is_paid:
        
        cupon,error = get_cupon(instance.order.discount_code) 
        if 'percent_off' in cupon and cupon.get('valid'):
            discount = order_total * ( cupon.get('percent_off') / 100)
            order_total=order_total - discount

    instance.order.paid_amount = order_total 
    instance.order.save()