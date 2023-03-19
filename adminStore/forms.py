from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('conversation','sender','receiver','content',)
        labels={
            'conversation':'',
            'sender':'',
            'receiver':'',
            'content':'',
        }
        widgets = {
            'conversation': forms.Select(attrs={
                'hidden':''
            }),
            'sender': forms.Select(attrs={
                'hidden':''
            }),
            'receiver': forms.Select(attrs={
                'hidden':''
            }),
            'content':forms.Textarea(attrs={
                'class':'form-control', 'rows':3, 'placeholder':'Message'
            }),
        }
        