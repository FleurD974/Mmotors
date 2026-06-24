from django import forms

from store.models import Document, Car

class DocumentForm(forms.ModelForm):
    
    class Meta:
        model = Document
        fields = ['file', 'type']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),

            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 'model', 'engine', 'mileage', 'passenger_number', 'is_purchased',
            'is_leased', 'purchase_price', 'leasing_price', 'registration_number', 'description'
        ]
        widgets = {
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'engine': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'passenger_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'is_purchased': forms.CheckboxInput(),
            'is_leased': forms.CheckboxInput(),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'leasing_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'description': forms.Textarea(),
        }
