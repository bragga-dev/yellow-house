from django.contrib import admin
from vitrine.models import ArtWork, ArtworkImage, ArtworkCategory, Souvenir, SouvenirCategory, SouvenirImage, BannerGroup, BannerImage


# ---------- Inline para imagens de Artwork ----------
class ArtworkImageInline(admin.TabularInline):
    model = ArtworkImage
    extra = 1
    readonly_fields = ('id',)
    fields = ('image', 'is_primary', 'id')
    autocomplete_fields = ()
    ordering = ('-is_primary', 'id')


# ---------- Admin de ArtWork ----------
@admin.register(ArtWork)
class ArtWorkAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'price', 'stock', 'created_at')
    search_fields = ('name', 'artist__user__username', 'art_work_category__name')
    list_filter = ('art_work_category', 'created_at')
    ordering = ('-created_at',)
    inlines = [ArtworkImageInline]  # adiciona as imagens inline


# ---------- Admin de ArtworkImage ----------
@admin.register(ArtworkImage)
class ArtworkImageAdmin(admin.ModelAdmin):
    list_display = ('artwork', 'image', 'is_primary')
    search_fields = ('artwork__name',)
    list_filter = ('is_primary',)
    ordering = ('-is_primary', 'id')
    readonly_fields = ('id',)
    autocomplete_fields = ('artwork',)


# ---------- Admin de ArtworkCategory ----------
@admin.register(ArtworkCategory)
class ArtworkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('slug',)


# ---------- Inline para imagens de Souvenir ----------
class SouvenirImageInline(admin.TabularInline):
    model = SouvenirImage
    extra = 1
    readonly_fields = ('id',)
    fields = ('image', 'is_primary', 'id')
    ordering = ('-is_primary', 'id')


# ---------- Admin de Souvenir ----------
@admin.register(Souvenir)
class SouvenirAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'size')
    search_fields = ('name', 'artist__user__username', 'souvenir_category__name')
    list_filter = ('souvenir_category', 'created_at')
    ordering = ('-created_at',)
    inlines = [SouvenirImageInline]  # adiciona as imagens inline


# ---------- Admin de SouvenirImage ----------
@admin.register(SouvenirImage)
class SouvenirImageAdmin(admin.ModelAdmin):
    list_display = ('souvenir', 'image', 'is_primary')
    search_fields = ('souvenir__name',)
    list_filter = ('is_primary',)
    ordering = ('-is_primary', 'id')
    readonly_fields = ('id',)
    autocomplete_fields = ('souvenir',)


# ---------- Admin de SouvenirCategory ----------
@admin.register(SouvenirCategory)
class SouvenirCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('slug',)


class BannerImageInline(admin.TabularInline):
    model = BannerImage
    extra = 1  # Quantas imagens extras mostrar para adicionar
    fields = ('image', 'is_primary')  # Campos a exibir
    readonly_fields = ()
    show_change_link = True  # Mostra link para editar imagem separadamente
    max_num = 10  # Limita a quantidade máxima de imagens

@admin.register(BannerGroup)
class BannerGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_images',)
    inlines = [BannerImageInline]
    search_fields = ('name',)

    def total_images(self, obj):
        return obj.images.count()
    total_images.short_description = "Quantidade de imagens"

# Caso queira registrar BannerImage separadamente também
@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ('group', 'is_primary', 'image')
    list_filter = ('group', 'is_primary')
    search_fields = ('group__name',)
