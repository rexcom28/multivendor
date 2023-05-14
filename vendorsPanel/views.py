from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy,reverse
from .models import Prices
from django.http import QueryDict
#store app
from store.decorator import is_vendor
from store.models import Product,Discount

#userprofie app
from userprofile.api_stripe import StripePrice

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PricesForm

@method_decorator(is_vendor(), name='dispatch')
class MyProducts_ListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'vendorsPanel/myProductList.html'
    context_object_name = 'productList'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            discounts = Discount.objects.filter(created_by=self.request.user)
            discount_filter = self.request.GET.get('discount_filter')
            if discount_filter:
                discounts = discounts.filter(code_name__icontains=discount_filter)
            context['discounts'] = discounts
        except:
            context['discounts'] = []

        try:
            prices = Prices.objects.filter(product__user=self.request.user)        
            context['prices'] = prices
        except:
            
            context['prices'] = []

        #al retornar de userprofile.EditDiscount_UpdateView retorna el discountTab para seleccionar la tab        
        if self.request.method =='GET' and self.request.GET.get('discountTab') != None :
            context['discountTab']=True
        elif self.request.method =='GET' and self.request.GET.get('pricesTab') != None :
            context['pricesTab']=True
        else:
            context['productTab']=True

        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        product_filter = self.request.GET.get('product_filter')        
        if product_filter:
            queryset = queryset.filter(title__icontains=product_filter)
        return queryset


class Prices_UpdateView(UpdateView):
    model = Prices
    form_class = PricesForm
    template_name = 'vendorsPanel/partials/PricesEdit.html'
    success_url = reverse_lazy('MyProducts_ListView')
    
    
    def get_success_url(self):
        url = super().get_success_url()
        query_dict =QueryDict(mutable=True)
        query_dict.update({'pricesTab':'active'})
        return f'{url}?{query_dict.urlencode()}'
    
    def form_valid(self, form):
        product = form.cleaned_data['product']
        price_id = form.cleaned_data['stripe_id']
        price_amount = form.cleaned_data['price_amount']
        active_price = form.cleaned_data['active_price']

        if active_price:#check if other price instance  from this product have the default price and uncheck
            prices = Prices.objects.filter(product=product)
            for price in prices:
                if price.active_price and price != self:
                    price.active_price=False
                    price.save()

        if price_amount == product.price:
            messages.error(self.request, 'the price can not be equals to the original price of product')
            return self.form_invalid(form)
        
        
        PriceAPI = StripePrice()
        priceObj, error = PriceAPI.editPrice(price_id, price_amount, active_price)

        if error:
            print(error)
            form.add_error(None, str(error))
            return self.form_invalid(form)
        

        return super().form_valid(form)

@method_decorator(is_vendor(), name='dispatch')
class Prices_CreateView(LoginRequiredMixin, CreateView):
    model = Prices
    form_class = PricesForm
    template_name = 'vendorsPanel/partials/PricesEdit.html'
    success_url = reverse_lazy('MyProducts_ListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method=='GET':            
            context['form']= PricesForm()
        return context
    
    def get_success_url(self):
        url = super().get_success_url()
        query_dict =QueryDict(mutable=True)
        query_dict.update({'pricesTab':'active'})    
        return f'{url}?{query_dict.urlencode()}'    
    
    def form_valid(self, form):
        product = form.cleaned_data['product']
        price_amount = form.cleaned_data['price_amount']

        
    
        PriceAPI = StripePrice()
        priceObj, error = PriceAPI.createPrice(product,price_amount,'usd')
        if error:
            print(error)
            form.add_error(None, str(error))
            return self.form_invalid(form)
        
        # Save the form with the stripe_id field set to the price ID
        
        form.instance.stripe_id = priceObj.id
        return super().form_valid(form)
    
@method_decorator(is_vendor(), name='dispatch')
class PricesFromProduct_CreateView( CreateView):

    model = Prices
    form_class = PricesForm
    template_name = 'vendorsPanel/partials/PricesEdit.html'
    success_url = reverse_lazy('MyProducts_ListView')

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['qs'] = Discount.objects.filter(created_by=self.request.user)
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        if product_id:
            product =Product.objects.get(id=product_id)
            ini = {'product': product, 'price_amount':product.price}
            context['form'] = PricesForm(initial=ini)        
        return context

    def get_success_url(self):
        url = super().get_success_url()
        query_dict =QueryDict(mutable=True)
        query_dict.update({'pricesTab':'active'})        
        return f'{url}?{query_dict.urlencode()}'
       
    def form_valid(self, form):
        product = form.cleaned_data['product']
        price_amount = form.cleaned_data['price_amount']
        active_price = form.cleaned_data['active_price']
        
        if price_amount == product.price:
            messages.error(self.request, 'the price can not be equals to the original price of product')
            return self.form_invalid(form)

        PriceAPI = StripePrice()
        priceObj, error = PriceAPI.createPrice(product,price_amount,'usd', active_price)
        if error:
            print(error)
            form.add_error(None, str(error))
            return self.form_invalid(form)
        
        # Save the form with the stripe_id field set to the price ID
        
        form.instance.stripe_id = priceObj.id
        return super().form_valid(form)
