import imp
from django.shortcuts import render
from store.models import Product
from store.decorator import verify_customer

def frontpage(request):
    products = Product.objects.filter(status=Product.ACTIVE)[0:6]
    return render(request, 'core/frontpage.html',{
        'products':products
    })

def frontpage2(request):
    products = Product.objects.filter(status=Product.ACTIVE)[0:6]
    return render(request, 'core/frontpage2.html',{
        'products':products
    })

def about(request):
    return render(request, 'core/about.html')