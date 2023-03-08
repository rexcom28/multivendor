from django.shortcuts import render
from .models import Shipped_Orders
from store.models import Order

#CVB
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import DetailView



class Shipping_ListView(ListView):
    paginate_by =50
    model = Shipped_Orders
    context_object_name = 'shipped_orders'
    template_name = 'Shipping/shippings_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.filter(is_paid=True)#, shipped_orders__isnull=False)#.distinct()
        context['orders'] = orders
        return context