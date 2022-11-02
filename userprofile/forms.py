from tkinter import Widget
from . models import Userprofile
from django.contrib.auth.models import User
from .models import Userprofile
from django import forms 

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )
        
        widgets={
            'first_name': forms.TextInput(attrs={
               'class':  'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'last_name': forms.TextInput(attrs={
               'class':  'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
            'email': forms.TextInput(attrs={
               'class':  'w-full mb-2 px-2 py-4 border border-gray-200'
            }),
        }
        
        
class ProfileForm(forms.ModelForm):
   #override the model declaration, where in model aren't required
   #but in form are required.
   #is_vendor = forms.BooleanField(required=True)
   
   class Meta:
      model = Userprofile
      help_texts = {
         'RFC': 'Enter you RFC only if you check vendor ',
      }
      fields = ('user', 'is_vendor','RFC',)
      widgets = {
         'user':forms.HiddenInput(),
         #'RFC':forms.HiddenInput(),
      }
      
      
      