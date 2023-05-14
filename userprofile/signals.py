from django.contrib.auth.models import User
from .models import customerProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

from userprofile.api_stripe import raw_create_customer

@receiver(post_save,sender=User)
def post_save_user(sender,instance,created,*args, **kwargs):
    try:
        customer = instance.customer
    except customerProfile.DoesNotExist:
        customer = None
    
    if customer is None:
        # Create a new customer object and associate it with the user
        customer, error = raw_create_customer()
        customerProfile.objects.create(user=instance, stripe_cus_id=customer.id)        
    # else:
    #     # The customer object exists, so you can perform any necessary updates
    #     if customer.stripe_cus_id == '':
    #         # Update the customer object with the new stripe_cus_id
    #         customer.stripe_cus_id = customer.id
    #         customer.save()
    #         print(customer, "customer retived")
                