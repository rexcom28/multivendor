from . models import Userprofile
from django.contrib.auth.models import User
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