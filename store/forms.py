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

        labels = {
            'brand': 'Marque',
            'model': 'Modèle',
            'engine': 'Motorisation',
            'mileage': 'Kilométrage',
            'passenger_number': 'Nombre de places',
            'is_purchased': 'À vendre',
            'is_leased': 'À louer',
            'purchase_price': 'Prix de vente',
            'leasing_price': 'Loyer mensuel',
            'registration_number': 'Immatriculation',
            'description': 'Description',
        }

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

    def clean(self):
        cleaned_data = super().clean()
        is_purchased = cleaned_data.get('is_purchased')
        is_leased = cleaned_data.get('is_leased')

        if is_purchased and is_leased:
            raise forms.ValidationError(
                'Une voiture ne peut pas être en location et à l\'achat.'
            )

        if not is_purchased and not is_leased:
            raise forms.ValidationError(
                'Une voiture doit être en location ou à l\'achat.'
            )

        return cleaned_data
