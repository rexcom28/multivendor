import stripe
from django.conf import settings

stripe.api_key=settings.STRIPE_SECRET_KEY

'''
CUSTOMERS
'''
def retrive_customer(customer_id:str):
    customer ={}    
    api_obj = stripe.Customer.retrieve(customer_id)
    customer,error = excepapi_obj(api_obj)
    
    if 'address' in customer.keys():
        address_flatten=customer.pop('address')
        customer.update(address_flatten)        
    if 'email' in customer.keys():
        customer['email2']=customer.pop('email')
    return customer , error

def update_customer(id,customer): 
    Semail=customer.pop('email2')
    Sname =customer.pop('name')
    Sphone=customer.pop('phone')
    Saddress = customer
    
    Sshipping={}        
    Sshipping['name']   =Sname
    Sshipping['phone']  =Sphone
    Sshipping['address']=customer
    
    api_obj = stripe.Customer.modify(
        f'{id}',
        address=Saddress,
        email=Semail,
        name=Sname,
        phone=Sphone,
        shipping=Sshipping
    )
    client,error =excepapi_obj(api_obj)
    return client.id, error
    

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
    
    api_obj = stripe.Customer.create(
        
        address=Saddress,
        email=Semail,
        name=Sname,
        phone=Sphone,
        shipping=Sshipping
    )
    client,error = excepapi_obj(api_obj)
    return client.id, error

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
    # Display a very generic error to the user, and maybe send
    # yourself an email
        return '', E
    except Exception as E:
    # Something else happened, completely unrelated to Stripe
        return '', E

    
    

def excepapi_obj(api_obj):
    try:
        obj=api_obj        
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

    return obj,''