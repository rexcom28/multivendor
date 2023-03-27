from django.conf import settings
from . models import Product
from userprofile.api_stripe import StripePrice


apiStripe = StripePrice()

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
            
        self.cart=cart
        
    
    def __iter__(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)
            self.cart[str(p)]['discount_code'] = self.cart[str(p)].get('discount_code', '')
            
        for item in self.cart.values():
            item['total_price'] = int(item['product'].price * item['quantity']) /100
            yield item
            
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
                        
    def add(self, product_id, quantity=1, update_quantity=False, discount_code=None):
        product_id = str(product_id)
    
        
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': int(quantity), 'id': product_id, 'discount_code':discount_code}
        
        if update_quantity:
                        
            self.cart[product_id]['quantity'] += int(quantity)

            if self.cart[product_id]['quantity'] == 0:
                self.remove(product_id)
            
        self.save()
    
    def remove(self, product_id):
        
        
        if product_id in self.cart:            
            
            del self.cart[product_id]       
            self.save()
    
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
    
    def get_total_cost(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)
        
        
        total_cost = 0
        discount = 0
        for item in self.cart.values():
            # Apply discount to the specific product
            if item['discount_code'] != None :
                if item['product'].discount.check_times_redeemed < item['product'].discount.stock:                    
                    total_cost += self.get_discount_amount(item, item['product'].discount.discount_percent, item['product'].price * item['quantity'])
            else:
                total_cost += item['product'].price * item['quantity']
                
        return int(total_cost) / 100
        #return int(sum(item['product'].price * item['quantity'] for item in self.cart.values())) / 100

    def get_discount_amount(self, item, discount_percent, total ):

        #price, error = apiStripe.createPrice(item) # type: ignore    
        discount = total - (total * (discount_percent/100))

        return discount
    
    def get_item(self, product_id):
        if str(product_id) in self.cart:
            return self.cart[str(product_id)]
        else:
            return None