

from django import forms
from . models import Product, Order, Discount

class OrderForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput)
    class Meta:
        model= Order        
        fields = (
            'first_name', 
            'last_name', 
            'address', 
            'zipcode', 
            'city',
            'id',
            'discount_code',
        )
        
        
class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('category', 'title', 'description', 'price', 'image', 'status','discount',)
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'description': forms.Textarea(attrs={
                'rows':3,
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'price': forms.TextInput(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
           
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'discount': forms.Select(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
        }

class DiscountForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = Discount
        exclude = ('created_at','modified_at',)
        widgets= {
            
            'created_by':forms.HiddenInput(),
            'code_name': forms.TextInput(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'desc': forms.Textarea(attrs={
                'rows':3,
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
        }