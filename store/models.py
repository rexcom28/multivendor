

from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from django.template.defaultfilters import slugify

from django.db.models import Sum

from io import BytesIO
from PIL import Image
from .validators import validate_file_extension, valid_ext_dict
from  userprofile.api_stripe import get_cupon

class Discount(models.Model):
    created_by = models.ForeignKey(User, related_name='discounts', on_delete=models.CASCADE)    
    code_name    = models.CharField(max_length=35, unique=True)
    desc    = models.TextField()
    stock   = models.IntegerField()
    times_redeemed= models.IntegerField(editable=False,blank=True,null=False,default=0)
    discount_percent = models.IntegerField()
    active  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
    #deleted_at = models.DateField(blank=True)

    @property
    def check_times_redeemed(self):
        times_redeemed = 0
        if self.code_name:
            times= get_cupon(self.code_name)
            if 'times_redeemed' in times[0]:
                times_redeemed = times[0]['times_redeemed']
                self.times_redeemed=times_redeemed
                self.save()
        return times_redeemed
    def __str__(self):
        return f'-Code:{self.code_name} -Discount %: {self.discount_percent}'



class Category(models.Model):
    
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50)
    
    class Meta:
        
        verbose_name_plural = 'Categories'
        
    def __str__(self):
       return self.title

    def save(self,*args, **kwargs):
        if self.title:
            self.slug=slugify(self.title)
        return super().save(*args,**kwargs)
    
    
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
    discount = models.ForeignKey(Discount, related_name='discount_id',on_delete=models.DO_NOTHING, null=True, blank=True)
    #discount = models.CharField(max_length=100,null=True, blank=True)
    id_stripe = models.CharField(max_length=100,blank=True, null=True, unique=True)
    
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
                return 'https://placehold.co/300x300/jpg'    
            
            
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
    

class CarouselImage(models.Model):
    product = models.ForeignKey('Product', related_name='carousel', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='carousel/')
    caption = models.CharField(max_length=100,blank=True)
    order = models.PositiveIntegerField()
    class Meta:
        ordering = ['order']

class Order(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    paid_amount = models.IntegerField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    payment_intent = models.CharField(max_length=255)
    discount_code = models.CharField(max_length=35, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_shipped = models.BooleanField(default=False)
    class Meta:
        ordering = ('-id','-created_at',)
        
    def get_display_price(self):
        return self.paid_amount /100
    
    def __str__(self):
        return f'{self.id}'



    # def save(self,*args, **kwargs):
    #     if self.order.is_paid:
    #         ord =self.order
    #         ord.is_shipped=True
    #         ord.save()
    #     super(Shipped_Orders,self).save(*args,**kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
        
    def get_display_price(self):
        return self.price / 100
    
    def get_item_total(self):
        return (self.price / 100) * self.quantity
    

class Product_Inventory(models.Model):
    product_id  = models.ForeignKey(Product, related_name='product_inv', on_delete=models.CASCADE)
    
    quantity    = models.IntegerField()
    created_at  = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
    #deleted_at = models.DateField(blank=True)
    # class Meta:        
    #     abstract =True

#this must be created with signal in orders
class Payment_Detail(models.Model):
    order_id    = models.ForeignKey(Order, related_name='payment_detail', on_delete=models.CASCADE)
    amount      = models.IntegerField()
    #provider can be another class with provider list or can be pyment type  
    provider    = models.CharField(max_length=35,blank=True)
    status      = models.CharField(max_length=10)
    created_at  = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)

    # class Meta:
    #     abstract=True

