import json 
import stripe
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from .models import Category, Product, Order, OrderItem
from .forms import OrderForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .cart import Cart



#-------------Cart functions

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect('cart_view')

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
def order_view(request, pk):
    
    order  = Order.objects.get(id=pk)    
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
        if request.is_ajax():
            res = {}
            res = list(Order.objects.values().filter(id=pk))
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

def product_detail(request, category_slug, slug):
    
    product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE) 
    
    return render(request, 'store/product_detail.html', {
        'product':product
    })
    
    
    
