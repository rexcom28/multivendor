from . models import Userprofile
from django.contrib.auth.models import User
from .models import Userprofile,customerProfile
from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import (
    password_validation,
)
from .api_stripe import *

inputs = '''
form-control
'''

class customerCreationForm(UserCreationForm):
   
   email = forms.EmailField(
      required=True,
      label="Email",
      max_length=254,
      widget=forms.EmailInput(attrs={'autocomplete': 'email','class':  inputs+' my_custom_selector'})
    )
   password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class':inputs}),
        help_text=password_validation.password_validators_help_text_html(),
    )
   password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class':inputs}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )
   class Meta:
      model = User
      fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2',)
      
      widgets={
         'username': forms.TextInput(attrs={
            'class':inputs,            
         }),
         
         'first_name': forms.TextInput(attrs={
            'class': inputs+' my_custom_selector',
                       
         }),
         'last_name': forms.TextInput(attrs={
            'class':  inputs+' my_custom_selector'
         }),
         'email': forms.TextInput(attrs={
            'class':  inputs+' my_custom_selector'
         }),
      }

class customerProfileForm(forms.ModelForm):
   city     = forms.CharField(label="Ciudad:",max_length=15,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   country  = forms.CharField(label="País:",max_length=2,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   line1    = forms.CharField(label="Calle/Numero:",max_length=35,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   line2    = forms.CharField(label="Descripciones/Referencias:",max_length=35,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   postal_code= forms.CharField(label="Código Postal:",max_length=5,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   state    = forms.CharField(label="Estado:",max_length=15,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   email2    = forms.EmailField(max_length=65,required=True,
      widget=forms.EmailInput(attrs={'class':inputs})
   )
   name     = forms.CharField(label="Nombre Comprador:",max_length=65, required=True,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   phone    = forms.CharField(label="Teléfono:",max_length=15,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   
   class Meta:
      model =customerProfile
      fields = ('stripe_cus_id', 'user', 'city', 'country','line1','line2','postal_code','state','email2','name','phone',)
      widgets = {
         'user': forms.HiddenInput(attrs={
               'class': inputs+' my_custom_selector'
         }),
         'stripe_cus_id': forms.HiddenInput(attrs={
               'class': inputs+' my_custom_selector'
         }),
      }
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['stripe_cus_id'].required = False

class customerSignUp(forms.Form):
   city     = forms.CharField(label="Ciudad:",max_length=15,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   country  = forms.CharField(label="País:",max_length=2,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   line1    = forms.CharField(label="Calle/Numero:",max_length=35,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   line2    = forms.CharField(label="Descripciones/Referencias:",max_length=35,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   postal_code= forms.CharField(label="Código Postal:",max_length=5,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   state    = forms.CharField(label="Estado:",max_length=15,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   email2    = forms.EmailField(max_length=65,required=True,
      widget=forms.EmailInput(attrs={'class':inputs})
   )
   name     = forms.CharField(label="Nombre Comprador:",max_length=65, required=True,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   phone    = forms.CharField(label="Teléfono:",max_length=15,required=False,
      widget=forms.TextInput(attrs={'class':inputs})
   )
   
class UserEditForm(forms.ModelForm):
    
    customer_profile_form = customerProfileForm()
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'email', )
        
        widgets={
            'first_name': forms.TextInput(attrs={
               'class':  inputs +' my_custom_selector'
            }),
            'last_name': forms.TextInput(attrs={
               'class': inputs +' my_custom_selector'
            }),
            'email': forms.TextInput(attrs={
               'class': inputs+' my_custom_selector'
            }),
        }


class Seller_Creation_Form(UserCreationForm):
   
   
   email = forms.EmailField(
      required=True,
      label="Email",
      max_length=254,
      widget=forms.EmailInput(attrs={'autocomplete': 'email','class':  inputs+' my_custom_selector'})
    )
   password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class':inputs}),
        help_text=password_validation.password_validators_help_text_html(),
    )
   password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class':inputs}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )
   class Meta:
      model = User
      fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2',)
      
      widgets={
         'username': forms.TextInput(attrs={
            'class':inputs,            
         }),
         
         'first_name': forms.TextInput(attrs={
            'class': inputs+' my_custom_selector',
                       
         }),
         'last_name': forms.TextInput(attrs={
            'class':  inputs+' my_custom_selector'
         }),
         'email': forms.TextInput(attrs={
            'class':  inputs+' my_custom_selector'
         }),
      }   

        
class ProfileForm(forms.ModelForm):
   #override the model declaration, where in model aren't required
   #but in form are required.
   is_vendor = forms.BooleanField(initial=True)
   stripe_cus_id = forms.CharField(widget=forms.HiddenInput(), required=False)
   class Meta:
      model = Userprofile
      help_texts = {
         'RFC': 'Enter you RFC only if you check vendor ',
      }
      fields = ('user', 'is_vendor','RFC', 'stripe_cus_id')
      widgets = {
         'user':forms.HiddenInput(),
         'RFC':forms.TextInput(attrs={
               'class': inputs+' my_custom_selector'
            }),        
      }

class UserAndProfileForm(Seller_Creation_Form, ProfileForm):
   RFC = forms.CharField( widget=forms.TextInput(attrs={'class':inputs+ ' my_custom_selector'}))
   is_vendor = forms.BooleanField(initial=True,label='', widget=forms.CheckboxInput(attrs={'class':'form control', 'hidden':''}))
   class Meta(Seller_Creation_Form.Meta, ProfileForm.Meta):
      model = User
      fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'is_vendor', 'RFC')
      widgets = {
         'user':forms.HiddenInput(),
         'RFC':forms.TextInput(attrs={
               'class': inputs+' my_custom_selector'
         }),
         'first_name':forms.TextInput(attrs={'class':inputs+' my_custom_selector' }),
         'last_name':forms.TextInput(attrs={'class':inputs+' my_custom_selector' }),
         'username':forms.TextInput(attrs={'class':inputs,}),

      }
      
   def save(self, commit=True):
      # Save the User model
      user = super().save(commit=False)
      user.save()

      # Save the Userprofile model
      userprofile = Userprofile.objects.create(user=user, is_vendor=self.cleaned_data['is_vendor'], RFC=self.cleaned_data['RFC'])
      userprofile.save()

      stripe_customer,err = vendor_customer(user)
      customerprofile=customerProfile.objects.create(user=user, stripe_cus_id=stripe_customer.id)      
      customerprofile.save()
      return user

      
    