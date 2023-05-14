from django.urls import path
from . import views

urlpatterns = [
    path('myProductList/',views.MyProducts_ListView.as_view(), name='MyProducts_ListView' ),

    path('priceCreate/',views.Prices_CreateView.as_view(), name='priceCreate' ),
    path('priceCreatefromProduct/<int:product_id>/',views.PricesFromProduct_CreateView.as_view(), name='priceCreateFromProduct' ),
    path('priceUpdate/<int:pk>/',views.Prices_UpdateView.as_view(), name='priceUpdate' ),


]