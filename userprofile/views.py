
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from . models import Userprofile
from .forms import UserEditForm, ProfileForm

from store.forms import ProductForm
from store.models import Product, OrderItem, Order

def vendor_detail(request, pk):
    user = User.objects.get(pk=pk)
    products =  user.products.filter(status = Product.ACTIVE)
    return render(request, 'userprofile/vendor_detail.html', {
        'user':user, 
        'products':products,
    })

@login_required
def my_store(request):
    products = request.user.products.exclude(status=Product.DELETED)
    order_items = OrderItem.objects.filter(product__user=request.user)
    return render(request, 'userprofile/my_store.html', {
        'products':products,
        'order_items':order_items
    })

@login_required
def my_store_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk )
    
    return render(request, 'userprofile/my_store_order_detail.html',{
        'order':order
    })

@login_required
def add_product(request):
    print(',m', request.method )
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        print(form.is_valid)
        if form.is_valid():
            title = request.POST.get('title')            
            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(title)
            product.save()
            messages.success(request, 'The product was added!')
            return redirect ('my_store')
    else:
        form = ProductForm()
    
    return render(request, 'userprofile/product_form.html',{
        'title':'Add',
        'form':form
    })

@login_required
def edit_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        #remove instance thumbnail to remake the thumbnail in the model 
        if 'image' in request.FILES:
            x = str(form.instance.thumbnail)
            if not x.replace(form.instance.thumbnail.field.upload_to, '') == str(request.FILES['image']):
                #print('xxxxx ',x.replace(form.instance.thumbnail.field.upload_to, ''), '---------', str(request.FILES['image']))
                #print('image' in request.FILES)
                #print(x.replace(form.instance.thumbnail.field.upload_to, ''))
                form.instance.thumbnail =None        
                print(request.FILES['image'])
                
        if form.is_valid():
            form.save()
            messages.success(request, 'The changes was saved!')
            return redirect ('my_store')
    else:    
        form = ProductForm(instance=product)

    return render(request, 'userprofile/product_form.html',{
        'title':'Edit',
        'product':product,
        'form':form
    })

@login_required
def delete_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()
    messages.success(request, 'The product was deleted!')
    return redirect('my_store')

@login_required
def myaccount(request):
    u = User.objects.get(pk=request.user.id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            redirect('myaccount')
    else:
        form = UserEditForm(instance=u)
            
    return render(request, 'userprofile/myaccount.html', {'form':form})
  
  
def sigup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)                
        # print(form['username'].value())
        # print(profile_form['is_vendor'].value())
        if form.is_valid():            
            
            user= form.save()
            profile = Userprofile.objects.create(
                user=user, 
                is_vendor=profile_form['is_vendor'].value(),
                RFC=profile_form['RFC'].value()
            )
            if profile:       
                login(request, user)
                return redirect('frontpage')
    else:
        form = UserCreationForm()
        profile_form = ProfileForm()
        
    return render(request, 'userprofile/signup.html', {
        'form':form,
        'profile_form':profile_form
    })
            