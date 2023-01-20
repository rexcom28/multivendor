from django.urls import path
from . import views 
urlpatterns =[
    path('search/', views.search, name="search"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/checkout/',views.checkout, name="checkout"),
    path('cart/success/', views.success, name='success'),
    path('cart/success/reorder/', views.re_order, name ='re_order'),
    path('cart/success/reorder/item/', views.change_quantity_order, name ='re_order_item'),
    path('cart/success/reorder/delete/', views.remove_from_re_order, name ='re_order_remove'),
    path('cart/success/reorder/verify_internal/', views.verify_internal, name ='verify_internal'),
    path('cart/success/verified/', views.verified, name='verified'),
    path('cart/success/Orders/<int:pk>/', views.order_view, name='order_view'),
    
        
    path('change-quantity/<str:product_id>', views.change_quantity, name='change_quantity'),
    path('remove-from-cart/<str:product_id>/',views.remove_from_cart, name='remove_from_cart'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:slug>/', views.product_detail, name='product_detail'),

    path('shipping/order/<int:pk>/', views.Shipped_Order_UpdateView.as_view(), name='shipped_orders'),
    
]