import json
from requests import delete 
import stripe
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from .models import Category, Product, Order, OrderItem, Shipped_Orders
from .forms import OrderForm, Shipped_Orders_Form
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .cart import Cart
from django.contrib import messages
from userprofile.api_stripe import retrive_customer
from .decorator import check_user_able_to_see_page,verify_customer
from userprofile.api_stripe import get_cupon,verify_payment_intent

#CVB
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView

#-------------Cart functions
@login_required
def order_view(request, pk):
    
    order  = Order.objects.get(id=int(pk))
    if request.method == 'POST':
        
        if request.is_ajax():            
            data = json.loads(request.body)
            
            order.first_name= data['first_name']
            order.last_name= data['last_name']
            order.address= data['address']
            order.zipcode= data['zipcode']
            order.city= data['city']
            order.save()
            return  JsonResponse({'order':data})  
        else:    
            
            form = OrderForm(request.POST, instance=order)
        
            if form.is_valid():
                form.save()
        return redirect ('success')
    else:
        print('1 GET request.is_ajax',request.is_ajax())
        if request.is_ajax():
            d = request.GET.get('del',False)
            res = {}
            
            if d:
                order = get_object_or_404(Order, id=int(pk))
                if order:
                    order.delete()                     
            else:                               
                res = list(Order.objects.values().filter(id=int(pk)))
            return  JsonResponse({'order': res})

        form = OrderForm(instance=order)
    return render(request, 'store/OrderForm.html',{
        'form':form,        
    })

def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart_view')

def cart_view(request):
    cart = Cart(request)
    return render(request, 'store/cart_view.html', {
        'cart':cart
    })


@login_required
@verify_customer()
def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect('cart_view')


class Shipped_Order_UpdateView(UpdateView):
    model = Shipped_Orders
    #form_class = Shipped_Orders_Form
    fields = '__all__'
    template_name = 'userprofile/logistic/shipped_orders.html'
    context_object_name ='shipping'


    

@login_required
@verify_customer()
def success(request):
    form = OrderForm()
    orders = Order.objects.filter(created_by=request.user)
    return render(request, 'store/success.html',{
        'form':form,
        'orders':orders
    })

def verified(request):
    orders = Order.objects.filter(created_by=request.user)
    
    if request.method == 'POST':
        data = json.loads(request.body)                
        stripe.api_key = settings.STRIPE_SECRET_KEY
        response, err =verify_payment_intent(data['payment_intent'])
        print('res', response)
        if err:
            messages.error(request, f'{err.error.message}')
            return JsonResponse({'error':f'{err.error.message}'},status=err.http_status)

        order = Order.objects.get(payment_intent=data['payment_intent'])
        order.is_paid = True if response.status=='succeeded' else False
        order.save()
        return JsonResponse({'verified':response.status})
    else:
        form = OrderForm()
    return render(request, 'store/success.html',{
        'form':form,
        'orders':orders
    })

def verify_internal(request):
    oid = request.GET.get('oid', '')    
    order = Order.objects.get(id=oid)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    response = stripe.PaymentIntent.retrieve(
        order.payment_intent,
    )
    
    order.is_paid = True if response.status=='succeeded' else False
    order.save()
    return redirect('success')

@login_required
@verify_customer()
def re_order(request):
    items = {}
    strip_items = []
    if request.method == 'POST':
        if request.is_ajax:            
            data = json.loads(request.body)
            first_name , last_name, address,zipcode, city, orderId, discount_code = data.values()
            
            if orderId and first_name and last_name and address and zipcode and city :
                Instance = Order.objects.get(id=orderId)
                form = OrderForm(data=data, instance = Instance )
                if not Instance.items.all():
                    messages.error(request, 'No hay productos en la orden de compra')
                    return JsonResponse({'error':'No hay productos en la orden de compra'},status=401)

                total_price = 0
                valid = form.is_valid()
                if valid:
                    for item in  Instance.items.all():                        
                        total_price += item.product.price * item.quantity
                        strip_items.append({
                            'price_data':{
                                'currency':'usd',
                                'product_data':{
                                    'name': item.product.title,                                    
                                },
                                'unit_amount': item.product.price
                            },
                            'quantity':item.quantity
                        })
                
                #begins coupon validation segment stripe
                if discount_code:
                    cupon,err = get_cupon(discount_code)
                    
                    if err:
                        messages.error(request, f'{err.error.message}')                        
                        return JsonResponse({'error':f'{err.error.message}'},status=401)
                    if 'valid' in cupon:
                        if cupon.get('valid',False) == False:
                            messages.error(request, 'The coupon its not valid')                        
                            return JsonResponse({'error':'The coupon its not valid'},status=401)

                if valid:  
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    params ={
                        'payment_method_types':['card'],
                        'line_items':strip_items,
                        'mode':'payment',
                        'success_url':f'{settings.WEB_SITE_URL}cart/success/reorder/verify_internal/?oid={orderId}',
                        'cancel_url':f'{settings.WEB_SITE_URL}cart/success/',
                    }
                    discount=0
                    if discount_code and 'valid' in cupon:
                        if cupon.get('valid',False):
                            params.update(
                                {'discounts':[{'coupon':f'{discount_code}'}],}
                            )
                            discount = cupon.get('percent_off',0) / 100
                            discount = total_price * discount

                    session = stripe.checkout.Session.create(
                        **params                
                    )
                    payment_intent = session.payment_intent
                    form.instance.payment_intent = payment_intent
                    form.instance.paid_amount = total_price - discount

                    form.save()
                    
            return JsonResponse({
                'session':session, 
                'order':payment_intent, 
                #'redirect':'/cart/success/'
            })
        # None Ajax call in POST    
        else:   
            #this section triggers if the function reOrder in orderForm.html 
            #take off the event.preventDefault             
            orders = Order.objects.get(id=request.POST['id'])            
            orderId= orders.id
            items  = orders.items.all()
            form   = OrderForm(request.POST, instance=orders)            
            if form.is_valid():            
                form.save()
            return redirect('success')    
    #------------End POST segment
    

    #------------GET start segment
    else:   
        orderId = request.GET.get('oid', '') 
        orders = Order.objects.get(id=orderId)
        
        if orders.first_name and orders.last_name:            
            items = orders.items.all()
            for item in items:
                strip_items.append({                    
                    'price_data':{
                        'currency':'usd',
                        'product_data':{
                            'name':item.product.title,
                        },
                        'unit_amount':item.price
                    },
                    'quantity':item.quantity
                })
        form = OrderForm(instance=orders, initial={'id':orderId})
    #change template to a edit order 
    
    return render(request, 'store/OrderForm.html',{
        'form':form,        
        'items':items,
        'orderId':orderId,
        'pub_key': settings.STRIPE_PUB_KEY
    })

@login_required#(login_url='/cart/checkout/')
@verify_customer()
def checkout(request):
    cart = Cart(request)
    
    if cart.get_total_cost() == 0:
        return redirect('cart_view')    
    if request.method == 'POST':
        
        if  request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request'})
        data = json.loads(request.body)
        first_name , last_name, address,zipcode, city, discount_code = data.values()     
        if first_name and last_name and address and zipcode and city :
            form = OrderForm(request.POST)
            
            total_price =0
            items = []
            for item in cart:

                product= item['product']
                total_price += product.price * int(item['quantity'])
                items.append({
                    'price_data':{
                        'currency': 'usd',
                        'product_data':{
                            'name': product.title,
                        },
                        'unit_amount': product.price
                    },
                    'quantity':item['quantity']
                })

            #begins cuopon validation segment
            cupon=''
            err=''
            if discount_code:                
                cupon,err = get_cupon(discount_code)
                if err:                    
                    messages.error(request, f'{err.error.message}')
                    return JsonResponse({'error':f'{err.error.message}'})
                if 'valid' in cupon:
                    if cupon.get('valid',False)==False:
                        messages.error(request, f'Coupon not valid!')
                        return JsonResponse({'error':f'Coupon not valid!'})
                    
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session=''
            payment_intent=''
            discount=0
            params={
                'payment_method_types':['card'],
                'line_items':items,
                'mode':'payment',                    
                'success_url':f'{settings.WEB_SITE_URL}cart/success/',
                'cancel_url':f'{settings.WEB_SITE_URL}cart/',
            }

            order_params = {
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "zipcode": zipcode,
                "city": city,
                "created_by": request.user,                
            
                "paid_amount":total_price - discount,
            }

            if discount_code and 'valid' in cupon:
                if cupon.get('valid',False):
                    params.update(
                        {'discounts':[{'coupon':f'{discount_code}'}],}
                    )

                    discount = cupon.get('percent_off',0) / 100
                    discount = total_price * discount
                    del order_params["paid_amount"]
                    order_params.update({
                        "discount_code":discount_code,
                        "paid_amount":total_price-discount,
                    })

            
            session = stripe.checkout.Session.create(
                **params
            )

            payment_intent = session.payment_intent
            if len(payment_intent) > 0:                
                order_params.update({"payment_intent": payment_intent,})
                
            order = Order.objects.create(
                **order_params
            )
            
            
            #create order
            for item in cart:
                product = item['product']
                quantity = int(item['quantity'])
                price = product.price * quantity                
                item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
            
            cart.clear()    
            
            return JsonResponse({'session':session, 'order':payment_intent}, status=200) #redirect('myaccount')
 
    else:
        cus = request.user
        init ={}
        if cus.customer.stripe_cus_id!='':
            customer, error= retrive_customer(cus.customer.stripe_cus_id)            
            if all([customer.get('name'), customer.get('line1'), customer.get('postal_code'), customer.get('city')]):
                init={
                    'first_name': customer.get('name') ,
                    'address':customer.get('line1'),
                    'zipcode':customer.get('postal_code'),
                    'city':customer.get('city')
                }
            if error!='':
                messages.error(request,error)

        form = OrderForm(initial=init)
    return render(request, 'store/checkout.html', {
        'cart':cart,
        'form':form,
        'pub_key': settings.STRIPE_PUB_KEY,
        'fullurl':settings.URL_API,
    })

def change_quantity(request, product_id):
    cart = Cart(request)
    action = request.GET.get('action', '')
    
    quantity = 1 if action=='increase' else -1
    cart.add(product_id, quantity, True)
    
    return redirect('cart_view')

def change_quantity_order(request):
    oid = request.GET.get('oid', '')
    item = request.GET.get('item', '')
    action = request.GET.get('action', '')
    
    order = Order.objects.get(id=int(oid))
    items = order.items.all().count()#filter(id=int(item))
    
    if order:
        oi = OrderItem.objects.get(id=int(item))        
        
        if action == 'increase':            
            oi.quantity +=1
        else:
            oi.quantity -=1  
                      
        if oi.quantity==0 and items==1:
            order.delete()
            return redirect('success')
        if oi.quantity==0 and items >1:    
            oi.delete()                  
            
        else:
            oi.save()
            
    url = reverse('re_order')    
    url += f'?oid={oid}'
    
    return redirect(url)

def remove_from_re_order(request):
    oid = request.GET.get('oid', '')
    item = request.GET.get('item', '')

    order = Order.objects.get(id=int(oid))
    items = order.items.all().count()
    oi = OrderItem.objects.get(id=int(item))  
    
    if order and oi:
        if items == 1:
            order.delete()
            messages.add_message(request, messages.INFO, 'Order deleted !')
            return redirect ('success')
        else:
            messages.add_message(request, messages.INFO, 'Item deleted !')
            oi.delete()            
        
    url = reverse('re_order')    
    url += f'?oid={oid}'
    
    return redirect(url)

#---------------------------------------------------
def search(request):
    query    = request.GET.get('query', '')
    products = Product.objects.filter(status=Product.ACTIVE).filter(
        Q(title__icontains=query)
        |
        Q(description__icontains=query)
    )
    
    return render(request, 'store/search.html',{
        'query':query ,
        'products':products                 
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(status=Product.ACTIVE)
    return render(request, 'store/category_detail.html', {
        'category':category,
        'products':products
    })

#@login_required
#@check_user_able_to_see_page('mirones')
#@verify_customer
def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE) 
    return render(request, 'store/product_detail.html', {
        'product':product
    })

#===================CLASS BASED VIEWS

class Category_ListView(ListView):
    paginate_by =10
    model = Category
    template_name = 'store/category/category_list.html'

    def get(self, request, *args, **kwargs):
        title_filter = request.GET.get('title_filter', '')
        self.queryset = self.model.objects.filter(title__icontains=title_filter)
        return super().get(request, *args, **kwargs)

class Category_CreateView(CreateView):
    model = Category
    template_name= 'store/category/create.html'
    fields = ['title']
    success_url = '/categories/list/'

class Category_UpdateView(UpdateView):
    model= Category
    template_name= 'store/category/create.html'
    fields = ['title']
    success_url = '/categories/list/'



