import stripe
from django.conf import settings

stripe.api_key=settings.STRIPE_SECRET_KEY

'''
CUSTOMERS
'''
def retrive_customer(customer_id:str):
    customer ={}  
    try:
        customer = stripe.Customer.retrieve(customer_id)
        if 'address' in customer.keys():
            address_flatten=customer.pop('address')
            customer.update(address_flatten)        
        if 'email' in customer.keys():
            customer['email2']=customer.pop('email')
        return customer , ''
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.APIConnectError as E:
        return '', E
    except stripe.error.StripeError as e:
    # Display a very generic error to the user, and maybe send
    # yourself an email
        return '', E
    except Exception as E:
    # Something else happened, completely unrelated to Stripe
        return '', E
    

def update_customer(id,customer): 
    Semail=customer.pop('email2')
    Sname =customer.pop('name')
    Sphone=customer.pop('phone')
    Saddress = customer
    
    Sshipping={}        
    Sshipping['name']   =Sname
    Sshipping['phone']  =Sphone
    Sshipping['address']=customer
    try:
        client = stripe.Customer.modify(
            f'{id}',
            address=Saddress,
            email=Semail,
            name=Sname,
            phone=Sphone,
            shipping=Sshipping
        )
        return client.id, 
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.APIConnectError as E:
        return '', E
    except stripe.error.StripeError as e:
    # Display a very generic error to the user, and maybe send
    # yourself an email
        return '', E
    except Exception as E:
    # Something else happened, completely unrelated to Stripe
        return '', E
    

#create customer
def create_customer(form, customer):
    Semail=customer.pop('email2')
    Sname =customer.pop('name')
    Sphone=customer.pop('phone')
    Saddress = customer
    
    Sshipping={}        
    Sshipping['name']   =Sname
    Sshipping['phone']  =Sphone
    Sshipping['address']=customer
    try:
        client = stripe.Customer.create(
            
            address=Saddress,
            email=Semail,
            name=Sname,
            phone=Sphone,
            shipping=Sshipping
        )
        
        return client.id, ''
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.APIConnectError as E:
        return '', E
    except stripe.error.StripeError as e:
    # Display a very generic error to the user, and maybe send
    # yourself an email
        return '', E
    except Exception as E:
    # Something else happened, completely unrelated to Stripe
        return '', E
'''
CUPONS
'''  
def create_cupon(data):
    try:
        obj= stripe.Coupon.create(
            id=data['code_name'],
            percent_off=data['discount_percent'],
            duration="repeating",
            duration_in_months=1,
            name=data['code_name'],
            max_redemptions=data['stock']
        )
        return obj,''
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.APIConnectError as E:
        return '', E
    except stripe.error.StripeError as e:    
        return '', E
    except Exception as E:    
        return '', E

def get_cupon(cupon_name):
    try:
        coupon = stripe.Coupon.retrieve(cupon_name)
        return coupon, ''
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.APIConnectError as E:
        return '', E
    except stripe.error.StripeError as e:    
        return '', E
    except Exception as E:    
        return '', E

def delete_cupon(cupon_name):
    try:
        del_cupon=stripe.Coupon.delete(cupon_name)

        return del_cupon,''
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.APIConnectError as E:
        return '', E
    except stripe.error.StripeError as e:    
        return '', E
    except Exception as E:    
        return '', E


def verify_payment_intent(payment_intent):
    try:
        res= stripe.PaymentIntent.retrieve(
            payment_intent,
        )
        return res,''
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.APIConnectError as E:
        return '', E
    except stripe.error.StripeError as e:    
        return '', E
    except Exception as E:    
        return '', E