from django.db import models
from store.models import Discount, Product

class Prices(models.Model):
    stripe_id = models.CharField(max_length=100, unique=True)    
    product = models.ForeignKey(Product, related_name='prices', on_delete=models.CASCADE)
    #discount = models.ForeignKey(Discount, related_name='discountPrice', on_delete=models.CASCADE)
    #price_stock = models.IntegerField()
    price_amount = models.IntegerField()
    active_price = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.product.title}'
    
    class Meta:
        ordering = ('product','-active_price',)