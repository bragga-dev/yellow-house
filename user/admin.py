# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username', 'email', 'cpf', 'phone', 'is_staff', 'is_active', 'photo')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'cpf')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'cpf', 'phone', 'photo')}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'cpf', 'phone', 'photo', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('cep', 'road', 'number', 'district', 'city', 'state', 'country')
    search_fields = ('cep', 'road', 'number', 'district', 'city', 'state', 'country')
    ordering = ('cep',)