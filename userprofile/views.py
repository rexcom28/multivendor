


from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.text import slugify
from . models import Userprofile
from .forms import UserEditForm

from store.forms import ProductForm
from store.models import Product

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
    
    return render(request, 'userprofile/my_store.html', {
        'products':products
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
        #print(form.instance.thumbnail)
        #print(request.FILES['image'])
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
        
        if form.is_valid():
            user= form.save()
            
            login(request, user)
            
            userprofile = Userprofile.objects.create(user=user)
            
            return redirect('frontpage')
    else:
        form = UserCreationForm()
        
    return render(request, 'userprofile/signup.html', {'form':form})
            