from django.db import models, transaction
from vitrine.validators import validate_image_file
from user.models import Artist
from django.core.exceptions import ValidationError
import uuid
from vitrine.utils import generate_unique_slug
from django.utils.translation import gettext_lazy as _  
from django.core.validators import MinValueValidator
from django.urls import reverse



class Package(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weight = models.FloatField(_('Peso'), help_text="Peso total em kg", null=False, blank=False, validators=[MinValueValidator(0.00)])
    width = models.FloatField(_('Largura'), help_text="Largura em cm", null=False, blank=False, validators=[MinValueValidator(0.00)])
    height = models.FloatField(_('Altura'), help_text="Altura em cm", null=False, blank=False, validators=[MinValueValidator(0.00)])
    length = models.FloatField(_('Comprimento'), help_text="Comprimento em cm", null=False, blank=False, validators=[MinValueValidator(0.00)])

    def clean(self):
        errors = {}

        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        weight = safe_float(self.weight)
        width = safe_float(self.width)
        height = safe_float(self.height)
        length = safe_float(self.length)

        if weight is not None and weight < 0:
            errors['weight'] = 'O peso não pode ser negativo.'
        if width is not None and width < 0:
            errors['width'] = 'A largura não pode ser negativa.'
        if height is not None and height < 0:
            errors['height'] = 'A altura não pode ser negativa.'
        if length is not None and length < 0:
            errors['length'] = 'O comprimento não pode ser negativo.'

        if errors:
            raise ValidationError(errors)

        return super().clean()

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    name = models.CharField(_('Nome'), max_length=200)
    description = models.TextField(_('Descrição'), null=True, blank=True)
    price = models.DecimalField(_('Preço'), max_digits=10, decimal_places=2,
            default=0.00, help_text="Preço em reais (R$).", null=False, blank=False, validators=[MinValueValidator(0.00)])
    stock = models.PositiveIntegerField(_('Estoque'), default=0, help_text="Quantidade em estoque.", null=False, blank=False, 
                                        validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name
    

    def clean(self):
        if self.price < 0:
            raise ValidationError({'price': 'O preço não pode ser negativo.'})
        if self.stock < 0:
            raise ValidationError({'stock': 'O estoque não pode ser negativo.'})
        

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name, self.id)
        super().save(*args, **kwargs)

   
class ArtworkCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nome'), max_length=100, unique=True)
   
    class Meta:
        verbose_name = "Categoria de obras"
        verbose_name_plural = "Categorias de obras"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    

class ArtWork(Product):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.OneToOneField(Package, on_delete=models.CASCADE, related_name='artworks', null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name='artworks')
    art_work_category = models.ForeignKey(ArtworkCategory, on_delete=models.PROTECT, related_name='artworks')
    width = models.FloatField(_('Largura (cm)'), null=False, blank=False)
    height = models.FloatField(_('Altura (cm)'), null=False, blank=False)
    technique = models.CharField(_('Técnica'), max_length=100, null=True, blank=True)
    year_created = models.DateField(_('Ano de criação'), null=True, blank=True)    
    style = models.CharField(_('Estilo'), max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("vitrine:detail_artwork", kwargs={"slug": self.slug, "artwork_id": self.id})

    
    class Meta:
        verbose_name = "Obra"
        verbose_name_plural = "Obras"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name, self.id)
        super().save(*args, **kwargs)


class SouvenirCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nome'), max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Souvenir Category"
        verbose_name_plural = "Souvenir Categories"
        ordering = ['name']

   
   
        
class Souvenir(Product):
    SIZE_CHOICES = [
        ('Pequeno', 'Pequeno'),
        ('Médio', 'Médio'),
        ('Grande', 'Grande'),
        ('Extra Grande', 'Extra Grande'),  
    ]

    souvenir_category = models.ForeignKey(SouvenirCategory, on_delete=models.PROTECT, related_name='souvenirs')
    material = models.CharField(_('Material'), max_length=100, null=True, blank=True)
    size = models.CharField(_('Tamanho'), max_length=20, choices=SIZE_CHOICES, null=True, blank=True)
    package = models.OneToOneField(Package, on_delete=models.CASCADE, related_name='souvenirs', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Souvenir"
        verbose_name_plural = "Souvenirs"
        ordering = ['name']
    
    def get_absolute_url(self):
        return reverse("vitrine:souvenir_detail",  kwargs={"slug": self.slug, "souvenir_id": self.id})
    
class ArtworkImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artwork = models.ForeignKey(ArtWork, on_delete=models.CASCADE, related_name='images', help_text="Imagens do produto.")
    image = models.ImageField(upload_to='artwork/', validators=[validate_image_file])
    is_primary = models.BooleanField(default=False)

    def clean(self):
        max_images = 5
        if not self.artwork_id:
            return
        if self.artwork.images.exclude(pk=self.pk).count() >= max_images:
            raise ValidationError(f"Uma obra não pode ter mais que {max_images} imagens.")

    def __str__(self):
        return f"Image for {self.artwork.name}"
    

    class Meta:
        verbose_name = "Product Image Artwork"
        verbose_name_plural = "Product Images Artworks"
        ordering = ['-is_primary', 'id']

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)  
        if self.is_primary:
            ArtworkImage.objects.filter(artwork=self.artwork, is_primary=True).exclude(pk=self.pk).update(is_primary=False)

                  


class SouvenirImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    souvenir = models.ForeignKey(Souvenir, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='souvenir/', validators=[validate_image_file])
    is_primary = models.BooleanField(default=False)


    def clean(self):
        max_images = 5
        if not self.souvenir_id:
            return  
        if self.souvenir.images.exclude(pk=self.pk).count() >= max_images:
            raise ValidationError({'image': f'Uma obra não pode ter mais que {max_images} imagens.'})


    def __str__(self):
        return f"Image for {self.souvenir.name}"
    
    class Meta:
        verbose_name = "Souvenir"
        verbose_name_plural = "Souvenirs"
        ordering = ['-is_primary', 'id']

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)  
        if self.is_primary:
            SouvenirImage.objects.filter(souvenir=self.souvenir, is_primary=True).exclude(pk=self.pk).update(is_primary=False)


class BannerGroup(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Banner Group"
        verbose_name_plural = "Banner Groups"

    def save(self, *args, **kwargs):
        with transaction.atomic():  # garante que tudo aconteça como uma transação
            super().save(*args, **kwargs)
            if self.is_active:
                BannerGroup.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)


class BannerImage(models.Model):
    group = models.ForeignKey(BannerGroup, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('Imagem'), upload_to='banners/', validators=[validate_image_file])
    is_primary = models.BooleanField(_('Imagem Principal'), default=False)

    class Meta:
        ordering = ['-is_primary', 'id']
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def __str__(self):
        return f"Banner for {self.group.name}"


class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Titulo'), max_length=100, blank=False, null=False)
    text = models.TextField(_('Texto'), blank=False, null=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    image = models.ImageField(_('Imagem'), upload_to='blog/', validators=[validate_image_file])
    is_published = models.BooleanField(_('Publicado?'), default=False)

    def __str__(self):
        return self.title
    

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse("vitrine:blog_detail", kwargs={"slug": self.slug, "blog_id": self.id})
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title, self.id)
        super().save(*args, **kwargs)