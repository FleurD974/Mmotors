from django import forms

from accounts.models import Customer

class UserForm(forms.ModelForm):
    
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "password"]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'last_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'email': forms.EmailInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'password': forms.PasswordInput(attrs={
                'class':"form-control",
                'style': 'max-width: 300px;'
            })
        }