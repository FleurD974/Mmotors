from django import forms

from store.models import Document

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
