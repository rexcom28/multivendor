from django.contrib import admin
from .models import (
    Category, 
    Product, 
    CarouselImage,
    Order, 
    OrderItem, 
    Shipped_Orders,
    Discount, 
    Product_Inventory, 
    Payment_Detail,
)
from django.conf import settings
import stripe





@admin.action(description='Verified payment')
def verified_payment(modeladmin,request,queryset):
    for p in queryset:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        response = stripe.PaymentIntent.retrieve(
            p.payment_intent,
        )
        paid = True if response.status=='succeeded' else False
        print('paid', paid, response.status)
        p.is_paid= paid
        p.save()
        

class OrderAdmin(admin.ModelAdmin):
    
    @admin.display(description='paid amount')
    def paid_amount_get(self, obj):
        return f'$ {str(obj.paid_amount /100)}'
    
    list_display = ['first_name', 'last_name','paid_amount', 'is_paid', 'created_by', 'is_shipped']
    search_fields = ['first_name','paid_amount', 'payment_intent','created_by_id__username', 'is_shipped']
    actions = [verified_payment]

class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image','caption']


class Discount_Admin(admin.ModelAdmin):
    list_display=['code_name','created_by','stock','times_redeemed', 'discount_percent']

class Product_Admin(admin.ModelAdmin):
    @admin.display(description='price')
    def price_get(self, obj):
        return f'$ {str(obj.price /100)}'
    list_display=['title','user', 'id_stripe','category', 'price_get','thumbnail','status','discount']


# class Shipped_Orders_Admin(admin.ModelAdmin):
#     list_display = ['order']

admin.site.register(Shipped_Orders)#,Shipped_Orders_Admin)
admin.site.register(Category)
admin.site.register(Product,Product_Admin)
admin.site.register(CarouselImage,CarouselImageAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Discount, Discount_Admin)
admin.site.register(Product_Inventory)
admin.site.register(Payment_Detail)
