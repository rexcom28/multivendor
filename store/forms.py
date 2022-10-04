

from django import forms
from . models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'title', 'description', 'price', 'image',)
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
           
            'image': forms.FileInput(attrs={
                'class': 'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
        }