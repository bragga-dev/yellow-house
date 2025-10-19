# checkout/forms.py
from django import forms
from checkout.models import Cart, CartItem
from vitrine.models import ArtWork, Souvenir

class CartItemForm(forms.ModelForm):
    souvenir = forms.ModelChoiceField(
        queryset=Souvenir.objects.filter(stock__gt=0),
        required=False,
        label='Souvenir',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    artwork = forms.ModelChoiceField(
        queryset=ArtWork.objects.filter(stock__gt=0),
        required=False,
        label='Artwork',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CartItem
        fields = ['souvenir', 'artwork', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('souvenir') and not cleaned_data.get('artwork'):
            raise forms.ValidationError("Selecione pelo menos um produto.")
        return cleaned_data


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = []  
