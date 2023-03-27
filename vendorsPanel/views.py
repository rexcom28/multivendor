from django.shortcuts import render
from django.views.generic.list import ListView

#store app
from store.decorator import is_vendor
from store.models import Product,Discount

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

@method_decorator(is_vendor(), name='dispatch')
class MyProducts_ListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'vendorsPanel/myProductList.html'
    context_object_name = 'productList'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['discounts'] = Discount.objects.filter(created_by=self.request.user)
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        product_filter = self.request.GET.get('product_filter')
        if product_filter:
            queryset = queryset.filter(title__icontains=product_filter)
        return queryset   
