from django import forms 
from .models import Prices

from store.models import Discount
from store.forms import ProductForm

inputs = """form-control"""
class PricesForm(forms.ModelForm):
    stripe_id =forms.CharField(widget=forms.HiddenInput, required=False)
    active_price = forms.BooleanField(required=False, help_text='Check if this will we the default price until you uncheck')
    
    class Meta:
        model = Prices
        fields = ('product','stripe_id', 'price_amount', 'active_price',)

        widgets ={
            'product':forms.Select(attrs={
                'class':inputs
            }),
            'price_amount':forms.NumberInput(attrs={
                'class':inputs
            }),
            'active_price':forms.CheckboxInput(attrs={
                'class':inputs
            })
        }    

# class ProductWithPriceDiscountForm(ProductForm, PricesForm):
#     discount_code = forms.CharField(max_length=35, required=False, label='Discount Code')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['discount'].required = False

#     def clean_discount_code(self):
#         code = self.cleaned_data['discount_code']
#         if code:
#             try:
#                 discount = Discount.objects.get(code_name=code, active=True)
#                 self.cleaned_data['discount'] = discount
#             except Discount.DoesNotExist:
#                 raise forms.ValidationError('Invalid discount code.')
#         return code

#     def save(self, commit=True):
#         product = super().save(commit=False)
#         stripe_price = 'idPirce1' #create_stripe_price(product.title, product.price, product.id_stripe)
#         price = super(PricesForm, self).save(commit=False)
#         price.stripe_id = stripe_price#['id']
#         price.product = product
#         if commit:
#             price.save()
#             product.save()
#         return product

#     class Meta(ProductForm.Meta):
#         fields = ProductForm.Meta.fields + ('discount_code',)
