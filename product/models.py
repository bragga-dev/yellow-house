from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name




class Product(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)

    # Imagem principal enviada para o MinIO
    imagem_principal = models.ImageField(upload_to='produtos/', blank=True, null=True)

    # URL da imagem (caso você queira referenciar diretamente em vez do .url)
    imagem_principal_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.imagem_principal:
            self.imagem_principal_url = self.imagem_principal.url
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class ImageProduct(models.Model):
    produto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/')
    legenda = models.CharField(max_length=100, blank=True)
    destaque = models.BooleanField(default=False)

    def __str__(self):
        return f"Imagem de {self.produto.nome}"
