from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import TabularInline, StackedInline
from .models import (
    DefaultAddress, Package, ArtworkCategory, ArtWork, 
    SouvenirCategory, Souvenir, ArtworkImage, SouvenirImage,
    BannerGroup, BannerImage, Blog
)


# ============ INLINES ============

class ArtworkImageInline(TabularInline):
    model = ArtworkImage
    extra = 1
    max_num = 5
    fields = ('image', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)
    verbose_name = _("Imagem da Obra")
    verbose_name_plural = _("Galeria de Imagens")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return _("Sem imagem")
    image_preview.short_description = _("Pré-visualização")


class SouvenirImageInline(TabularInline):
    model = SouvenirImage
    extra = 1
    max_num = 5
    fields = ('image', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)
    verbose_name = _("Imagem do Souvenir")
    verbose_name_plural = _("Galeria de Imagens")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return _("Sem imagem")
    image_preview.short_description = _("Pré-visualização")


class BannerImageInline(TabularInline):
    model = BannerImage
    extra = 1
    max_num = 10
    fields = ('image', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)
    verbose_name = _("Imagem do Banner")
    verbose_name_plural = _("Imagens do Banner")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="40" style="object-fit: cover;" />', obj.image.url)
        return _("Sem imagem")
    image_preview.short_description = _("Pré-visualização")


# ============ MODEL ADMINS ============

@admin.register(DefaultAddress)
class DefaultAddressAdmin(admin.ModelAdmin):
    list_display = ('cep', 'city', 'state', 'district', 'street', 'number')
    list_filter = ('state', 'city')
    search_fields = ('cep', 'city', 'state', 'district', 'street')
    fieldsets = (
        (_('Informações do Endereço'), {
            'fields': ('cep', 'city', 'state')
        }),
        (_('Detalhes do Local'), {
            'fields': ('district', 'street', 'number', 'complement')
        }),
    )


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'package_weight', 'package_width', 'package_height', 'package_length', 'artwork_link', 'souvenir_link')
    list_filter = ('package_weight',)
    search_fields = ('id',)
    fields = (('package_weight', 'package_width'), ('package_height', 'package_length'))
    readonly_fields = ('artwork_link', 'souvenir_link')
    
    def artwork_link(self, obj):
        if hasattr(obj, 'artworks'):
            artwork = obj.artworks
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:vitrine_artwork_change', args=[artwork.id]),
                artwork.name
            )
        return _("Não vinculado a obra")
    artwork_link.short_description = _("Obra Vinculada")
    
    def souvenir_link(self, obj):
        if hasattr(obj, 'souvenirs'):
            souvenir = obj.souvenirs
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:vitrine_souvenir_change', args=[souvenir.id]),
                souvenir.name
            )
        return _("Não vinculado a souvenir")
    souvenir_link.short_description = _("Souvenir Vinculado")
    
    def has_delete_permission(self, request, obj=None):
        # Prevenir exclusão se o pacote estiver sendo usado
        if obj and (hasattr(obj, 'artworks') or hasattr(obj, 'souvenirs')):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(ArtworkCategory)
class ArtworkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'artworks_count')
    search_fields = ('name',)

    def artworks_count(self, obj):
        return obj.artworks.count()
    artworks_count.short_description = _('Número de Obras')


@admin.register(ArtWork)
class ArtWorkAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'art_work_category', 'price', 'stock', 'created_at', 'is_available')
    list_filter = ('art_work_category', 'artist', 'created_at', 'style')
    search_fields = ('name', 'description', 'artist__user__username', 'technique')
    readonly_fields = ('slug', 'created_at', 'image_gallery', 'package_link')
    prepopulated_fields = {'name': ()}
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'slug', 'description', 'artist', 'art_work_category')
        }),
        (_('Detalhes da Obra'), {
            'fields': (('width', 'height'), 'technique', 'style', 'year_created')
        }),
        (_('Informações Comerciais'), {
            'fields': ('price', 'stock', 'created_at')
        }),
        (_('Pacote e Embalagem'), {
            'fields': ('package', 'package_link')
        }),
        (_('Galeria'), {
            'fields': ('image_gallery',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ArtworkImageInline]
    
    def package_link(self, obj):
        if obj.package:
            return format_html(
                '<a href="{}">Editar Pacote #{}</a>',
                reverse('admin:vitrine_package_change', args=[obj.package.id]),
                obj.package.id
            )
        return _("Nenhum pacote vinculado")
    package_link.short_description = _("Link para Pacote")
    
    def is_available(self, obj):
        return obj.stock > 0
    is_available.boolean = True
    is_available.short_description = _('Disponível')
    
    def image_gallery(self, obj):
        images = obj.images.all()[:5]
        html = ''
        for image in images:
            html += format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; margin: 5px;" />',
                image.image.url
            )
        return format_html(html) if html else _("Nenhuma imagem cadastrada")
    image_gallery.short_description = _('Galeria de Imagens')


@admin.register(SouvenirCategory)
class SouvenirCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'souvenirs_count')
    search_fields = ('name',)

    def souvenirs_count(self, obj):
        return obj.souvenirs.count()
    souvenirs_count.short_description = _('Número de Souvenirs')


@admin.register(Souvenir)
class SouvenirAdmin(admin.ModelAdmin):
    list_display = ('name', 'souvenir_category', 'price', 'stock', 'size', 'material', 'is_available')
    list_filter = ('souvenir_category', 'size', 'created_at')
    search_fields = ('name', 'description', 'material')
    readonly_fields = ('slug', 'created_at', 'image_gallery', 'package_link')
    prepopulated_fields = {'name': ()}
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'slug', 'description', 'souvenir_category')
        }),
        (_('Características'), {
            'fields': ('material', 'size', 'default_address')
        }),
        (_('Informações Comerciais'), {
            'fields': ('price', 'stock', 'created_at')
        }),
        (_('Pacote e Embalagem'), {
            'fields': ('package', 'package_link')
        }),
        (_('Galeria'), {
            'fields': ('image_gallery',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SouvenirImageInline]
    
    def package_link(self, obj):
        if obj.package:
            return format_html(
                '<a href="{}">Editar Pacote #{}</a>',
                reverse('admin:vitrine_package_change', args=[obj.package.id]),
                obj.package.id
            )
        return _("Nenhum pacote vinculado")
    package_link.short_description = _("Link para Pacote")
    
    def is_available(self, obj):
        return obj.stock > 0
    is_available.boolean = True
    is_available.short_description = _('Disponível')
    
    def image_gallery(self, obj):
        images = obj.images.all()[:5]
        html = ''
        for image in images:
            html += format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; margin: 5px;" />',
                image.image.url
            )
        return format_html(html) if html else _("Nenhuma imagem cadastrada")
    image_gallery.short_description = _('Galeria de Imagens')


@admin.register(BannerGroup)
class BannerGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'images_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('images_preview',)
    
    fieldsets = (
        (_('Informações do Grupo'), {
            'fields': ('name', 'is_active')
        }),
        (_('Pré-visualização das Imagens'), {
            'fields': ('images_preview',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BannerImageInline]
    
    def images_count(self, obj):
        return obj.images.count()
    images_count.short_description = _('Número de Imagens')
    
    def images_preview(self, obj):
        images = obj.images.all()[:3]
        html = ''
        for image in images:
            html += format_html(
                '<div style="display: inline-block; margin: 10px; text-align: center;">'
                '<img src="{}" width="120" height="60" style="object-fit: cover; border: 1px solid #ddd;" />'
                '<br><small>{}</small>'
                '</div>',
                image.image.url,
                _("Principal") if image.is_primary else _("Secundária")
            )
        return format_html(html) if html else _("Nenhuma imagem cadastrada")
    images_preview.short_description = _('Pré-visualização do Banner')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'text')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'image_preview_large')
    list_editable = ('is_published',)
    prepopulated_fields = {'title': ()}
    
    fieldsets = (
        (_('Conteúdo Principal'), {
            'fields': ('title', 'slug', 'text', 'image')
        }),
        (_('Metadados'), {
            'fields': ('is_published', 'created_at', 'updated_at')
        }),
        (_('Pré-visualização'), {
            'fields': ('image_preview_large',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return _("Sem imagem")
    image_preview.short_description = _("Imagem")
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="max-height: 200px; object-fit: contain;" />', obj.image.url)
        return _("Sem imagem")
    image_preview_large.short_description = _("Pré-visualização da Imagem")


# ============ REGISTRO DE MODELOS SEM CUSTOM ADMIN ============

@admin.register(ArtworkImage)
class ArtworkImageAdmin(admin.ModelAdmin):
    list_display = ('artwork', 'image_preview', 'is_primary')
    list_filter = ('is_primary', 'artwork__art_work_category')
    search_fields = ('artwork__name',)
    list_editable = ('is_primary',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return _("Sem imagem")
    image_preview.short_description = _("Pré-visualização")


@admin.register(SouvenirImage)
class SouvenirImageAdmin(admin.ModelAdmin):
    list_display = ('souvenir', 'image_preview', 'is_primary')
    list_filter = ('is_primary', 'souvenir__souvenir_category')
    search_fields = ('souvenir__name',)
    list_editable = ('is_primary',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return _("Sem imagem")
    image_preview.short_description = _("Pré-visualização")


@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ('group', 'image_preview', 'is_primary')
    list_filter = ('is_primary', 'group')
    search_fields = ('group__name',)
    list_editable = ('is_primary',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="40" style="object-fit: cover;" />', obj.image.url)
        return _("Sem imagem")
    image_preview.short_description = _("Pré-visualização")