from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import TabularInline, StackedInline
from .models import (
    User, Client, Artist, ClientAddress, ArtistAddress, Exhibitions
)


# ============ INLINES ============

class ClientAddressInline(TabularInline):
    model = ClientAddress
    extra = 1
    max_num = 5
    fields = ('cep', 'road', 'number', 'district', 'city', 'state', 'principal', 'complement')
    verbose_name = _("Endereço do Cliente")
    verbose_name_plural = _("Endereços do Cliente")


class ArtistAddressInline(TabularInline):
    model = ArtistAddress
    extra = 1
    max_num = 5
    fields = ('cep', 'road', 'number', 'district', 'city', 'state', 'principal', 'complement')
    verbose_name = _("Endereço do Artista")
    verbose_name_plural = _("Endereços do Artista")


class ExhibitionsInline(TabularInline):
    model = Exhibitions
    extra = 1
    max_num = 10
    fields = ('title', 'date', 'location', 'exhibition_banner_preview')
    readonly_fields = ('exhibition_banner_preview',)
    verbose_name = _("Exposição")
    verbose_name_plural = _("Exposições do Artista")

    def exhibition_banner_preview(self, obj):
        if obj.exhibition_banner:
            return format_html('<img src="{}" width="50" height="30" style="object-fit: cover;" />', obj.exhibition_banner.url)
        return _("Sem banner")
    exhibition_banner_preview.short_description = _("Banner")


# ============ MODEL ADMINS ============

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_artist', 'is_client', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_artist', 'is_client', 'is_staff', 'is_active', 'date_joined', 'is_trusty')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'cpf')
    readonly_fields = ('slug', 'date_joined', 'last_login', 'created_at', 'updated_at', 'photo_preview')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'slug')
        }),
        (_('Informações Pessoais'), {
            'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'cpf', 'phone', 'photo', 'photo_preview')
        }),
        (_('Permissões e Status'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_trusty',
                'is_artist', 'is_client', 'groups', 'user_permissions'
            )
        }),
        (_('Datas Importantes'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return _("Sem foto")
    photo_preview.short_description = _("Pré-visualização da Foto")

    def get_inline_instances(self, request, obj=None):
        # Mostra inlines baseado no tipo de usuário
        if obj and obj.is_client:
            return [ClientAddressInline(self.model, self.admin_site)]
        elif obj and obj.is_artist:
            return [ArtistAddressInline(self.model, self.admin_site)]
        return []


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'wants_to_be_artist', 'addresses_count', 'user_is_active')
    list_filter = ('wants_to_be_artist', 'user__is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user_link', 'addresses_list')
    inlines = [ClientAddressInline]
    
    fieldsets = (
        (_('Informações do Cliente'), {
            'fields': ('user', 'user_link', 'wants_to_be_artist')
        }),
        (_('Endereços'), {
            'fields': ('addresses_list',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:user_user_change', args=[obj.user.id]),
            obj.user.get_full_name()
        )
    user_link.short_description = _("Link para Usuário")
    
    def addresses_count(self, obj):
        return obj.addresses.count()
    addresses_count.short_description = _('Número de Endereços')
    
    def user_is_active(self, obj):
        return obj.user.is_active
    user_is_active.boolean = True
    user_is_active.short_description = _('Usuário Ativo')
    
    def addresses_list(self, obj):
        addresses = obj.addresses.all()[:5]
        if not addresses:
            return _("Nenhum endereço cadastrado")
        
        html = '<ul>'
        for address in addresses:
            html += format_html(
                '<li>{} - {}{}</li>',
                address.road,
                address.number,
                f" ({_('Principal')})" if address.principal else ""
            )
        html += '</ul>'
        return format_html(html)
    addresses_list.short_description = _("Endereços Cadastrados")


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'social_links_count', 'exhibitions_count', 'user_is_active')
    list_filter = ('is_verified', 'user__is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'bio')
    readonly_fields = ('user_link', 'banner_preview', 'social_links', 'exhibitions_list')
    inlines = [ArtistAddressInline, ExhibitionsInline]
    
    fieldsets = (
        (_('Informações do Artista'), {
            'fields': ('user', 'user_link', 'is_verified', 'bio')
        }),
        (_('Redes Sociais'), {
            'fields': ('instagram', 'facebook', 'twitter', 'tiktok', 'social_links'),
            'classes': ('collapse',)
        }),
        (_('Banner'), {
            'fields': ('banner', 'banner_preview')
        }),
        (_('Exposições'), {
            'fields': ('exhibitions_list',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:user_user_change', args=[obj.user.id]),
            obj.user.get_full_name()
        )
    user_link.short_description = _("Link para Usuário")
    
    def banner_preview(self, obj):
        if obj.banner:
            return format_html('<img src="{}" width="200" height="80" style="object-fit: cover;" />', obj.banner.url)
        return _("Sem banner")
    banner_preview.short_description = _("Pré-visualização do Banner")
    
    def social_links_count(self, obj):
        count = sum([
            1 if obj.instagram else 0,
            1 if obj.facebook else 0,
            1 if obj.twitter else 0,
            1 if obj.tiktok else 0
        ])
        return count
    social_links_count.short_description = _('Redes Sociais')
    
    def exhibitions_count(self, obj):
        return obj.exhibitions.count()
    exhibitions_count.short_description = _('Exposições')
    
    def user_is_active(self, obj):
        return obj.user.is_active
    user_is_active.boolean = True
    user_is_active.short_description = _('Usuário Ativo')
    
    def social_links(self, obj):
        links = []
        if obj.instagram:
            links.append(format_html('<li>Instagram: <a href="{}" target="_blank">{}</a></li>', obj.instagram, obj.instagram))
        if obj.facebook:
            links.append(format_html('<li>Facebook: <a href="{}" target="_blank">{}</a></li>', obj.facebook, obj.facebook))
        if obj.twitter:
            links.append(format_html('<li>Twitter: <a href="{}" target="_blank">{}</a></li>', obj.twitter, obj.twitter))
        if obj.tiktok:
            links.append(format_html('<li>TikTok: <a href="{}" target="_blank">{}</a></li>', obj.tiktok, obj.tiktok))
        
        if not links:
            return _("Nenhuma rede social cadastrada")
        
        return format_html('<ul>{}</ul>', ''.join(links))
    social_links.short_description = _("Links das Redes Sociais")
    
    def exhibitions_list(self, obj):
        exhibitions = obj.exhibitions.all()[:5]
        if not exhibitions:
            return _("Nenhuma exposição cadastrada")
        
        html = '<ul>'
        for exhibition in exhibitions:
            html += format_html(
                '<li><a href="{}">{}</a> - {}</li>',
                reverse('admin:user_exhibitions_change', args=[exhibition.id]),
                exhibition.title,
                exhibition.date
            )
        html += '</ul>'
        return format_html(html)
    exhibitions_list.short_description = _("Últimas Exposições")


@admin.register(ClientAddress)
class ClientAddressAdmin(admin.ModelAdmin):
    list_display = ('client', 'road', 'number', 'city', 'state', 'principal', 'created_at')
    list_filter = ('state', 'principal', 'created_at')
    search_fields = ('client__user__username', 'client__user__first_name', 'road', 'city', 'district')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'client_link')
    
    fieldsets = (
        (_('Informações do Endereço'), {
            'fields': ('client', 'client_link', 'principal')
        }),
        (_('Localização'), {
            'fields': ('cep', 'road', 'number', 'complement', 'district', 'city', 'state', 'country')
        }),
        (_('Metadados'), {
            'fields': ('slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:user_client_change', args=[obj.client.id]),
            obj.client.user.get_full_name()
        )
    client_link.short_description = _("Link para Cliente")


@admin.register(ArtistAddress)
class ArtistAddressAdmin(admin.ModelAdmin):
    list_display = ('artist', 'road', 'number', 'city', 'state', 'principal', 'created_at')
    list_filter = ('state', 'principal', 'created_at')
    search_fields = ('artist__user__username', 'artist__user__first_name', 'road', 'city', 'district')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'artist_link')
    
    fieldsets = (
        (_('Informações do Endereço'), {
            'fields': ('artist', 'artist_link', 'principal')
        }),
        (_('Localização'), {
            'fields': ('cep', 'road', 'number', 'complement', 'district', 'city', 'state', 'country')
        }),
        (_('Metadados'), {
            'fields': ('slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def artist_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:user_artist_change', args=[obj.artist.id]),
            obj.artist.user.get_full_name()
        )
    artist_link.short_description = _("Link para Artista")


@admin.register(Exhibitions)
class ExhibitionsAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'date', 'location', 'banner_preview')
    list_filter = ('date', 'artist__is_verified')
    search_fields = ('title', 'description', 'artist__user__first_name', 'location')
    readonly_fields = ('slug', 'banner_preview_large', 'artist_link')
    
    fieldsets = (
        (_('Informações da Exposição'), {
            'fields': ('artist', 'artist_link', 'title', 'slug', 'description')
        }),
        (_('Detalhes do Evento'), {
            'fields': ('date', 'location')
        }),
        (_('Banner da Exposição'), {
            'fields': ('exhibition_banner', 'banner_preview_large')
        }),
    )
    
    def banner_preview(self, obj):
        if obj.exhibition_banner:
            return format_html('<img src="{}" width="50" height="30" style="object-fit: cover;" />', obj.exhibition_banner.url)
        return _("Sem banner")
    banner_preview.short_description = _("Banner")
    
    def banner_preview_large(self, obj):
        if obj.exhibition_banner:
            return format_html('<img src="{}" width="300" height="150" style="object-fit: cover;" />', obj.exhibition_banner.url)
        return _("Sem banner")
    banner_preview_large.short_description = _("Pré-visualização do Banner")
    
    def artist_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:user_artist_change', args=[obj.artist.id]),
            obj.artist.user.get_full_name()
        )
    artist_link.short_description = _("Link para Artista")