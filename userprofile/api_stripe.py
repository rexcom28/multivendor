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
    # except stripe.error.APIConnectError as E:
    #     return '', E
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
        return client.id, ''
    except stripe.error.InvalidRequestError as E:
        return '', E
    except stripe.error.StripeError as E:
        return '', E
    except Exception as E:
    # Something else happened, completely unrelated to Stripe
        return '', E

def vendor_customer(user):
    try:
        return stripe.Customer.create(email=user.email), ''
    except stripe.error.StripeError as e:
        return None, StripeErrorHandler.handle_error(e)
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
    # except stripe.error.APIConnectError as E:
    #     return '', E
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
    # except stripe.error.APIConnectError as E:
    #     return '', E
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
    # except stripe.error.APIConnectError as E:
    #     return '', E
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
    # except stripe.error.APIConnectError as E:
    #     return '', E
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
    # except stripe.error.APIConnectError as E:
    #     return '', E
    except stripe.error.StripeError as e:    
        return '', E
    except Exception as E:    
        return '', E




'''----------------------Products----------'''

class StripeAPI:

    def create_product(self,product):
        try:
            
            product_api = {
                #'id':product.id,
                'active': True if product.status=='active' else False,                
                'description':product.description,
                'name':product.title,
            }     

            product_ =stripe.Product.create(**product_api)
            print(product_)
            price_api={
                "unit_amount":product.price,
                "currency":'usd',                
                "product":product_.id,                
            }
            price   = stripe.Price.create(
                **price_api
            )
            print('price created',price)
            return  product_, ''
        except stripe.error.StripeError as e:
            return None, StripeErrorHandler.handle_error(e)
    
    def retrive_product(self,product):
        pass

    def get_price(self,product):
        try:
            return stripe.Price.list(product=f'{product.id}')
        except stripe.error.StripeError as e:
            return None, StripeErrorHandler.handle_error(e)
    
    def update_price(self,price, new_price):
        try:
            return stripe.Price.modify(price, active=False), ''
        except stripe.error.StripeError as e:
            return None, StripeErrorHandler.handle_error(e)

    def edit_product(self,product):
        try:                    
            return stripe.Product.modify(
                f'{product.id}',
                active=True if product.status=='active' else False,
                description=product.description,
                name=product.title
            ), ''
        except stripe.error.StripeError as e:
            return None, StripeErrorHandler.handle_error(e)

    def delete_product(self,product_id):
        '''
        this method only archive product in stripe api,
        since the documentation says this, this is a soft edit
        '''
        try:            
            return stripe.Product.modify(product_id,active=False), ''
        except stripe.error.StripeError as e:
            return None, StripeErrorHandler.handle_error(e)




class StripeErrorHandler:
    @staticmethod
    def handle_error(e):
        if isinstance(e,stripe.error.CardError):
            # Since it's a decline, stripe.error.CardError will be caught
            print(f'Status is: {e.http_status}')
            print(f'Type is: {e.error.type}')
            print(f'Code is: {e.error.code}')
            # param is '' in this case
            print(f'Param is: {e.error.param}')
            print(f'Message is: {e.error.message}')
        elif isinstance(e, stripe.error.RateLimitError):
            # Too many requests made to the API too quickly
            print('Rate limit error')
        elif isinstance(e, stripe.error.InvalidRequestError):
            # Invalid parameters were supplied to Stripe's API
            print('Invalid request error')
        elif isinstance(e, stripe.error.AuthenticationError):
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            print('Authentication error')
        elif isinstance(e, stripe.error.APIConnectionError):
            # Network communication with Stripe failed
            print('API connection error')
        elif isinstance(e, stripe.error.StripeError):
            # Display a very generic error to the user, and maybe send
            # yourself an email
            print('Stripe error')
        else:
            # Something else happened, completely unrelated to Stripe
            print('Other error')
        return e

