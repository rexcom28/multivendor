from django.db import models
from store.models import Product

class Prices(models.Model):
    stripe_id = models.CharField(max_length=100, unique=True)    
    product = models.ForeignKey(Product, related_name='prices', on_delete=models.CASCADE)
    

