import json
from requests import delete 
import stripe
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from .models import Category, Product, Order, OrderItem
from .forms import OrderForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .cart import Cart

from .decorator import check_user_able_to_see_page


#-------------Cart functions
@login_required
def order_view(request, pk):
    
    order  = Order.objects.get(id=int(pk))    
    if request.method == 'POST':
        
        if request.is_ajax():    
            print('is_ajax post ')        
            data = json.loads(request.body)
            print(data)
            order.first_name= data['first_name']
            order.last_name= data['last_name']
            order.address= data['address']
            order.zipcode= data['zipcode']
            order.city= data['city']
            order.save()
            return  JsonResponse({'order':data})  
        else:    
            print('no is_ajax') 
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

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect('cart_view')


@login_required
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
        response = stripe.PaymentIntent.retrieve(
            data['payment_intent'],
        )
        print(response)
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

@login_required
def re_order(request):
    
    
    items = {}
    strip_items = []
    if request.method == 'POST':
        if request.is_ajax:            
            data = json.loads(request.body)
            first_name , last_name, address,zipcode, city, orderId = data.values()
            print(request.POST)
            if orderId and first_name and last_name and address and zipcode and city :
                form = OrderForm(data=data)
                print(form.is_valid(),form.errors)
                
                return JsonResponse({
                    'session':'session', 
                    'order':'payment_intent', 
                    'redirect':'/cart/success/'
                })
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
        'orderId':orderId
    })

@login_required#(login_url='/cart/checkout/')
def checkout(request):
    cart = Cart(request)
    if cart.get_total_cost() == 0:
        return redirect('cart_view')
    
    if request.method == 'POST':
        data = json.loads(request.body)
        first_name , last_name, address,zipcode, city = data.values()        
        
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
            
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=items,
                mode='payment',
                success_url=f'{settings.WEB_SITE_URL}cart/success/',
                cancel_url =f'{settings.WEB_SITE_URL}cart/'
                
            )
            payment_intent = session.payment_intent
            
            order = Order.objects.create(
                first_name = first_name,
                last_name  = last_name,
                address    = address,
                zipcode    = zipcode,
                city       = city,
                created_by = request.user,
                #is_paid = True,
                payment_intent = payment_intent,
                paid_amount = total_price
            )
            
            
            #create order
            for item in cart:
                product = item['product']
                quantity = int(item['quantity'])
                price = product.price * quantity
                
                item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
            
            cart.clear()    
        
            return JsonResponse({'session':session, 'order':payment_intent}) #redirect('myaccount')
 
    else:    
        form = OrderForm()
    return render(request, 'store/checkout.html', {
        'cart':cart,
        'form':form,
        'pub_key': settings.STRIPE_PUB_KEY
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
    
    
    print(oid,'  ',item,' ',action)
    order = Order.objects.get(id=int(oid))
    items = order.items.all().filter(id=int(item))
    
    if order and items:
        oi = OrderItem.objects.get(id=int(item))        
        print('oi', oi)
        if action == 'increase':            
            oi.quantity +=1
        else:
            oi.quantity -=1            
        if oi.quantity==0:
            order.delete()
                  
            return redirect('success')
        else:
            oi.save()
            
    url = reverse('re_order')    
    url += f'?oid={oid}'
    print(url)
    return redirect(url)

def remove_from_re_order(request):
    oid = request.GET.get('oid', '')
    item = request.GET.get('item', '')
    print(f'{oid}, {item}')
    return redirect('success')

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
    
@login_required
@check_user_able_to_see_page('mirones')
def product_detail(request, category_slug, slug):
    
    product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE) 
    
    return render(request, 'store/product_detail.html', {
        'product':product
    })
    
    
    
