from django.db import models
from store.models import Order

class Shipped_Orders(models.Model):
    order = models.ForeignKey(Order, related_name='shipped_orders', on_delete=models.CASCADE)
    carrier_name = models.CharField(max_length=255)
    tracking_number = models.CharField(max_length=255)
    status = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    delivery_company = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ('id',)