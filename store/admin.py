from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.action(description='Verified payment')
def verified_payment(modeladmin,request,queryset):
    pass

class OrderAdmin(admin.ModelAdmin):
    
    @admin.display(description='paid amount')
    def paid_amount_get(self, obj):
        return f'$ {str(obj.paid_amount /100)}'
    
    list_display = ['first_name', 'last_name','paid_amount_get', 'is_paid', 'created_by']
    search_fields = ['first_name','paid_amount', 'payment_intent','created_by_id__username']

admin.site.register(Category)
admin.site.register(Product)

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)

