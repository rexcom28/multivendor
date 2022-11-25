from django.contrib import admin
from .models import (
    Category, 
    Product, 
    Order, 
    OrderItem, 
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
    
    list_display = ['first_name', 'last_name','paid_amount', 'is_paid', 'created_by']
    search_fields = ['first_name','paid_amount', 'payment_intent','created_by_id__username']
    actions = [verified_payment]

admin.site.register(Category)
admin.site.register(Product)

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Discount)
admin.site.register(Product_Inventory)
admin.site.register(Payment_Detail)
