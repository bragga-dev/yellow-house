from allauth.account.forms import SignupForm
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User
from validate_docbr import CPF
from .models import Address


class CustomSignupForm(SignupForm):
    email = forms.EmailField(label='E-mail', required=True)
    first_name = forms.CharField(max_length=30, label='Nome')
    last_name = forms.CharField(max_length=30, label='Sobrenome')
    username = forms.CharField(max_length=15, label='Nome de usuário')
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a senha', widget=forms.PasswordInput)

    # Esta propriedade garante que o formulário seja tratado como multipart para upload de arquivos
    is_multipart = True
    
    
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas não coincidem.")
        return cleaned_data


    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        
        user.save()
        return user


class UserUpdateForm(forms.ModelForm):


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'cpf', 'phone', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Digite seu nome'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Digite seu sobrenome'}),
            'username': forms.TextInput(attrs={'placeholder': 'Nome de usuário'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Apenas números'}),
            'phone': forms.TextInput(attrs={'placeholder': 'DDD + número'}),
            'photo': forms.ClearableFileInput(attrs={'placeholder': 'Foto de perfil'}),
        }

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



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'cpf', 'phone', 'photo')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'cpf', 'phone', 'photo')



# Endereço

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['cep', 'road', 'number', 'district', 'city', 'state', 'country']


class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['cep', 'road', 'number', 'district', 'city', 'state', 'country']
