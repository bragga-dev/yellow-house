
from django import forms
from vitrine.models import  ArtworkCategory, SouvenirCategory, ArtWork, Souvenir, ArtworkImage, SouvenirImage



class ArtworkCategoryForm(forms.ModelForm):
    class Meta:
        model = ArtworkCategory
        fields = ['name']   
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da categoria'}),

        }

class SouvenirCategoryForm(forms.ModelForm):
    class Meta:
        model = SouvenirCategory
        fields = ['name']   
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da categoria'}),
            
        }   

class ArtWorkForm(forms.ModelForm):
    class Meta:
        model = ArtWork
        fields = ['name', 'description', 'price', 'art_work_category', 'width', 'height', 'technique', 'year_created', 'style', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da obra'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição da obra', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço da obra'}),
            'art_work_category': forms.Select(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Largura em cm'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Altura em cm'}),
            'technique': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Técnica utilizada'}),
            'year_created': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Ano de criação', 'type': 'date'}),
            'style': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estilo da obra'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade em estoque'}),
            
        }   

class SouvenirForm(forms.ModelForm):
    class Meta:
        model = Souvenir
        fields = ['name', 'description', 'price', 'souvenir_category',  'material', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do souvenir'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição do souvenir', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço do souvenir'}),
            'souvenir_category': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Peso em gramas'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dimensões (ex: 10x5x2 cm)'}),
            'material': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material do souvenir'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade em estoque'}),
        }


class ArtworkImageForm(forms.ModelForm):
    class Meta:
        model = ArtworkImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SouvenirImageForm(forms.ModelForm):
    class Meta:
        model = SouvenirImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Buscar obras, souvenirs ou artistas...'
    }))
