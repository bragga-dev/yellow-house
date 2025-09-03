from django.db import models
from vitrine.models import validate_image_file
from user.models import Artist
from django.core.exceptions import ValidationError
import uuid
from django.utils.text import slugify   

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.id}")
            unique_slug = base_slug
            num = 1
            while self.__class__.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

class Artwork(Product):
    width = models.FloatField()
    height = models.FloatField()
    technique = models.CharField(max_length=100, null=True, blank=True)
    year_created = models.DateField(null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name='artworks')
    style = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name    
    
    class Meta:
        verbose_name = "Artwork"
        verbose_name_plural = "Artworks"
        ordering = ['name']



class SouvenirCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    image = models.ImageField(upload_to='souvenir_categories/', validators=[validate_image_file], null=False, blank=False)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while SouvenirCategory.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)
        
class Souvenir(Product):
    SIZE_CHOICES = [
        ('Pequeno', 'Pequeno'),
        ('Médio', 'Médio'),
        ('Grande', 'Grande'),
        ('Extra Grande', 'Extra Grande'),  
    ]

    souvenir_category = models.ForeignKey(SouvenirCategory, on_delete=models.PROTECT, related_name='souvenirs')
    material = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, null=False, blank=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Souvenir"
        verbose_name_plural = "Souvenirs"
        ordering = ['name']
        
    
class ProductImageArtwork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='images', help_text="Imagens do produto.")
    image = models.ImageField(upload_to='artwork/', validators=[validate_image_file])
    is_primary = models.BooleanField(default=False)

    def clean(self):
        max_images = 5
        if self.artwork.images.exclude(pk=self.pk).count() >= max_images:
            raise ValidationError(f"Um produto não pode ter mais que {max_images} imagens.")    

    def __str__(self):
        return f"Image for {self.artwork.name}"
    

    class Meta:
        verbose_name = "Product Image Artwork"
        verbose_name_plural = "Product Images Artworks"
        ordering = ['-is_primary', 'id']

class ProductImageSouvenir(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    souvenir = models.ForeignKey(Souvenir, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='souvenir/', validators=[validate_image_file])
    is_primary = models.BooleanField(default=False)


    def clean(self):
        max_images = 5
        if self.souvenir.images.exclude(pk=self.pk).count() >= max_images:
            raise ValidationError(f"Um produto não pode ter mais que {max_images} imagens.")  

    def __str__(self):
        return f"Image for {self.souvenir.name}"
    
    class Meta:
        verbose_name = "Product Image Souvenir"
        verbose_name_plural = "Product Images Souvenirs"
        ordering = ['-is_primary', 'id']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Salva primeiro para garantir que self.pk exista
        if self.is_primary:
            # Desmarca as outras imagens primárias do mesmo souvenir
            ProductImageSouvenir.objects.filter(souvenir=self.souvenir, is_primary=True).exclude(pk=self.pk).update(is_primary=False)


class BannerGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, editable=False)

    def __str__(self):
        return self.name

class BannerImage(models.Model):
    group = models.ForeignKey(BannerGroup, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='banners/', validators=[validate_image_file])
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f"Banner for {self.group.name}"
    
    def clean(self):
        max_images = 5
        if self.group.images.exclude(pk=self.pk).count() >= max_images:
            raise ValidationError(f"Um grupo de banners não pode ter mais que {max_images} imagens.")
