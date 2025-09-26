# admin.py

from django.contrib import admin
from .models import Client, ClientAddress, User
from .forms import CustomUserCreationForm, CustomUserChangeForm
admin.site.site_header = "Casa Amarela Admin"
admin.site.site_title = "Casa Amarela Admin"
admin.site.index_title = "Bem-vindo ao painel de administração Casa Amarela"


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Client, Artist, ClientAddress, ArtistAddress
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Inline para endereços do cliente
class ClientAddressInline(admin.TabularInline):
    model = ClientAddress
    extra = 1

# Inline para endereços do artista
class ArtistAddressInline(admin.TabularInline):
    model = ArtistAddress
    extra = 1

# Admin para User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'username', 'first_name', 'last_name', 'is_client', 'is_artist', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_client', 'is_artist', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'cpf', 'phone')
    ordering = ('email',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'cpf', 'phone', 'photo', 'date_of_birth')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_client', 'is_artist', 'is_trusty', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
        
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'cpf', 'phone', 'photo', 'password1', 'password2'),
        }),
    )

# Admin para Client com endereço inline
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = [ClientAddressInline]

# Admin para Artist com endereço inline e controle de is_verified
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified')
    list_filter = ('is_verified',)
    inlines = [ArtistAddressInline]

    
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_staff:
            return ('is_verified',)
        return ()
    
    # Filtrar apenas artistas válidos (user.is_artist=True)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_artist=True)

# Registrar endereços separadamente, se quiser:
@admin.register(ClientAddress)
class ClientAddressAdmin(admin.ModelAdmin):
    list_display = ('client', 'road', 'number', 'city', 'state', 'principal')

@admin.register(ArtistAddress)
class ArtistAddressAdmin(admin.ModelAdmin):
    list_display = ('artist', 'road', 'number', 'city', 'state', 'principal')
