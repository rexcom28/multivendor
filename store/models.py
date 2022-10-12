


from wsgiref.validate import validator
from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from django.template.defaultfilters import slugify


from io import BytesIO
from PIL import Image
from .validators import validate_file_extension, valid_ext_dict

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
    slug = models.SlugField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='uploads/product_images/', blank=True, null=True, validators=[validate_file_extension])
    thumbnail = models.ImageField(upload_to='uploads/product_images/thumbnail/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=ACTIVE)
    
    class Meta:
        ordering = ('-created_at', )
    
    def __str__(self):
        return self.title
    
    
    #overriden method for slug file
    def save(self, *args, **kwargs):
        
        self.slug = slugify(self.title)
        # print('self._state.adding---',self._state.adding)
        # print(self.thumbnail,'!= ',args)
        # print(kwargs)
        return super().save(*args, **kwargs)
        
    def get_display_price(self):
        return self.price /100
    
    
    def get_thumbnail(self):
        #print(self.thumbnail.url,' -------=====  ',self.thumbnail.field.upload_to)
        if self.thumbnail:
            origin= self.thumbnail.field.upload_to
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return self.thumbnail.url
            else:
                return 'https://via.placeholder.com/240x240x.jpg'    
            
            
    def make_thumbnail(self, image, size=(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        thumb_io = BytesIO()
        #check formats -> python -m PIL
        ext = valid_ext_dict.get(f".{image.name.split('.')[-1]}")
        
        img.save(thumb_io, ext, quality=85)
        name = image.name.replace('uploads/product_images/', '')
        thumbnail = File(thumb_io, name=name)

        return thumbnail
    
    
    
class Order(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    
    paid_amount = models.IntegerField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    payment_intent = models.CharField(max_length=255)
    
    created_by = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('-created_at',)
        
    def get_display_price(self):
        return self.paid_amount /100
    # def __str__(self) -> str:
    #     return f'Name: {self.first_name} Last Name: {self.last_name}    --- is paid ?: {self.is_paid}   --- id: {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
    
    # def __str__(self) -> str:
    #     return f'Order: {self.order.id}-----, Product: {self.product} x {self.quantity}'
    
    def get_display_price(self):
        return self.price /100