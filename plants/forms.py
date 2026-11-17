"""
Forms for the Plants application.
"""

from django import forms
from .models import Plant

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = [
            'name',
            'scientific_name',
            'category',
            'description',
            'morphology',
            'identification_features',
            'traditional_uses',
            'image',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tulsi'}),
            'scientific_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Ocimum sanctum'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'morphology': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'identification_features': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'traditional_uses': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
