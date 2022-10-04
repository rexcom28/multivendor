from distutils.command.upload import upload
from email.policy import default
from pyexpat import model
from random import choices
from tabnanny import verbose
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    
    class Meta:
        
        verbose_name_plural = 'Categories'
        
    def __str__(self):
       return self.title
        
    
    
class Product(models.Model):
    DRAFT = 'draft'
    WAITING_APPROVAL ='waitingaproval'
    ACTIVE='active'
    DELETED='deleted'
    
    STATUS_CHOICES =(
        (DRAFT, 'Draft'),
        (WAITING_APPROVAL, 'Waiting approval'),
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted'),
    )
    user = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='uploads/product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=ACTIVE)
    
    class Meta:
        ordering = ('-created_at', )
    
    def __str__(self):
        return self.title
    
    def get_display_price(self):
        return self.price /100