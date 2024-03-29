
from django.contrib.auth import  views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.sigup, name='signup'),
    path('customer_signup/', views.customer_signup, name='customer_signup'),
    path('login/', auth_views.LoginView.as_view(template_name='userprofile/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('myaccount/', views.myaccount, name='myaccount'),
    path('my-store/', views.my_store, name='my_store'),
    path('my-store/order-detail/<int:pk>/', views.MyStore_Order_DetailView.as_view(),  name="my_store_order_detail"),
    #path('my-store/order-detail/<int:pk>/', views.my_store_order_detail,  name="my_store_order_detail"),
    path('my-store/add-product/', views.add_product, name='add_product'),
    
    path('my-store/edit-product/<int:pk>/', views.ProductUpdateView.as_view(), name='edit_product'),
    path('my-store/delete-product/<int:pk>/', views.delete_product, name='delete_product'),    
    path('vendors/products/<int:pk>/', views.vendor_detail, name='vendor_detail'),    
    path('discount/', views.discount_view, name='discount_view'),
    path('editDiscount/<int:pk>/',views.EditDiscount_UpdateView.as_view(), name='editDiscount'),
    path('addDiscount/',views.AddDiscount_CreateView.as_view(), name='addDiscount'),

    
    path('check_code_name/', views.check_code_name, name='check_code_name'),
    path('customer/update/<str:pk>/', views.CustomerUpdateView.as_view(), name='stripe_CustomerUpdateView'),
    path('customer/create/<str:pk>/',views.create_customer_already_signup.as_view(),name='create_customer_already_signup'),
]
