from allauth.account.forms import SignupForm
from django import forms
from .models import Client, Artist, Exhibitions
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User
from validate_docbr import CPF
from .models import ClientAddress, ArtistAddress
from phonenumber_field.formfields import PhoneNumberField


class ClientSignupForm(SignupForm):
    email = forms.EmailField(label='E-mail', required=True)
    username = forms.CharField(max_length=15, label='Nome de usuário')
    first_name = forms.CharField(max_length=30, label='Nome')
    last_name = forms.CharField(max_length=30, label='Sobrenome')
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        validator = CPF(repeated_digits=True)
        if not validator.validate(cpf):
            raise forms.ValidationError("CPF inválido.")
        return cpf

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Telefone já está em uso.")
        return phone

    def save(self, request):
        user = super().save(request)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_client = True
        user.save()
        Client.objects.create(user=user)
        return user


# Artist 

class ArtistSignupForm(SignupForm):
    email = forms.EmailField(label='E-mail', required=True)
    username = forms.CharField(max_length=15, label='Nome de usuário')
    first_name = forms.CharField(max_length=30, label='Nome')
    last_name = forms.CharField(max_length=30, label='Sobrenome')

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        validator = CPF(repeated_digits=True)
        if not validator.validate(cpf):
            raise forms.ValidationError("CPF inválido.")
        return cpf

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Telefone já está em uso.")
        return phone

    def save(self, request):
        user = super().save(request)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_artist = False
        user.save()
        Artist.objects.create(user=user)
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'cpf', 'phone', 'photo', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Digite seu nome'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Digite seu sobrenome'}),
            'username': forms.TextInput(attrs={'placeholder': 'Nome de usuário'}),
            'date_of_birth': forms.DateInput(attrs={'placeholder': 'DD/MM/AAAA', 'type': 'date'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Apenas números'}),
            'phone': forms.TextInput(attrs={'placeholder': 'DDD + número'}),
            'photo': forms.ClearableFileInput(attrs={'placeholder': 'Foto de perfil'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dob = self.instance.date_of_birth
        if dob:
            self.initial['date_of_birth'] = dob.strftime('%Y-%m-%d')

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            cpf_validator = CPF(repeated_digits=True)
            if not cpf_validator.validate(cpf):
                raise forms.ValidationError("CPF inválido")
        return cpf
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            qs = User.objects.filter(phone=phone).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Este telefone já está em uso por outro usuário.")
        return phone



class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["wants_to_be_artist"]  
        widgets = {
            'wants_to_be_artist': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ArtistUpdateForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['is_verified', 'bio', 'banner', 'instagram', 'facebook', 'twitter', 'tiktok']
        widgets = {
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Conte um pouco sobre você.', 'rows': 4}),
            'banner': forms.ClearableFileInput(attrs={'placeholder': 'Formato de arquivo: jpg, jpeg ou png.'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'Link do seu perfil no Instagram.'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'Link do seu perfil no Facebook.'}),
            'twitter': forms.URLInput(attrs={'placeholder': 'Link do seu perfil no Twitter.'}),
            'tiktok': forms.URLInput(attrs={'placeholder': 'Link do seu perfil no TikTok.'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)

        if not self.user or not self.user.is_staff:
            self.fields['is_verified'].disabled = True

    def clean_is_verified(self):
        if not self.user or not self.user.is_staff:
            return self.instance.is_verified
        return self.cleaned_data.get('is_verified')


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'cpf', 'phone', 'photo')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'cpf', 'phone', 'photo')



class AddressForm(forms.ModelForm):
    class Meta:
        model = ClientAddress  # padrão, pode ser alterado dinamicamente
        fields = ['cep', 'road', 'number', 'district', 'city', 'state', 'country', 'complement', 'principal']
        widgets = {
            'cep': forms.TextInput(attrs={'placeholder': 'CEP'}),
            'road': forms.TextInput(attrs={'placeholder': 'Rua'}),
            'number': forms.TextInput(attrs={'placeholder': 'Número'}),
            'district': forms.TextInput(attrs={'placeholder': 'Bairro'}),
            'city': forms.TextInput(attrs={'placeholder': 'Cidade'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.TextInput(attrs={'placeholder': 'País'}),
            'complement': forms.TextInput(attrs={'placeholder': 'Complemento (opcional)'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        address_type = kwargs.pop('address_type', 'client')  # 'artist' ou 'client'
        self.address_type = address_type
        super().__init__(*args, **kwargs)
        if address_type == 'artist':
            self._meta.model = ArtistAddress
        else:
            self._meta.model = ClientAddress

    def save(self, commit=True, owner=None):  # <- adicionamos o owner (client ou artist)
        instance = super().save(commit=False)
        if owner:
            if self.address_type == 'client':
                instance.client = owner
            else:
                instance.artist = owner
        if commit:
            instance.save()
        return instance

class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibitions
        fields = ['artist', 'title', 'description', 'date', 'location']
        widgets = {
            'artist': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'placeholder': 'Título da exposição'}),
            'description': forms.Textarea(attrs={'placeholder': 'Descrição da exposição', 'rows': 4}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.TextInput(attrs={'placeholder': 'Local da exposição'}),   
        }

class PromoteToArtistForm(forms.Form):
    confirm = forms.BooleanField(label="Desejo me tornar um artista", required=True)

class DemoteToClientForm(forms.Form):
    confirm = forms.BooleanField(label="Desejo voltar a ser um cliente", required=True)


