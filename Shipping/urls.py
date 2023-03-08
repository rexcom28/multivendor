from django.urls import path
from . import views 
urlpatterns =[
    path('shippingList/', views.Shipping_ListView.as_view(), name='shipping_list')
]