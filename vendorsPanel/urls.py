from django.urls import path
from . import views

urlpatterns = [
    path('myProductList/',views.MyProducts_ListView.as_view(), name='MyProducts_ListView' ),
]