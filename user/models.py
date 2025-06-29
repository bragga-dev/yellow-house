import re
import uuid
from django.conf import settings
from django.db import models
from django.core import validators
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import imghdr
from django.urls import reverse
from django.utils.text import slugify
from validate_docbr import CPF
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError(_('The given username must be set'))
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  #
    username = models.CharField( _('username'), max_length=15, unique=True,
        help_text=_('Required. 15 characters or fewer. Letters, numbers and @/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(
                re.compile(r'^[\w.@+-]+$'),
                _('Enter a valid username.'),
                _('invalid')
            )
        ]
    )
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    photo = models.ImageField(upload_to="photos/", default="photos/default.jpg", blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)    
    phone = PhoneNumberField(max_length=15, unique=True, null=True, blank=True, help_text='Digite um número com DDD. Ex: +55 11 91234-5678')
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_trusty = models.BooleanField(
        _('trusty'),
        default=False,
        help_text=_('Designates whether this user has confirmed his account.')
    )
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'cpf']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'uuid': str(self.id), 'slug': self.slug})
    
    def save(self, *args, **kwargs):
        # Verificar se é um objeto novo ou se o nome mudou
        if not self.slug or self._state.adding or self.has_name_changed():
            base_slug = slugify(self.get_full_name())
            unique_slug = base_slug
            num = 1
            while User.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug

        # Chamada única ao método save do modelo base
        super().save(*args, **kwargs)
    
    def has_name_changed(self):
        """Verifica se o nome do usuário mudou"""
        if not self.id:
            return False
            
        old_user = User.objects.filter(id=self.id).first()
        if not old_user:
            return True
            
        return (old_user.first_name != self.first_name or 
                old_user.last_name != self.last_name)


class Address(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        cep = models.CharField(max_length=9, null=False)  
        road = models.CharField(max_length=255, null=False, blank=False)
        number = models.CharField(max_length=10, null=False, blank=False)
        district = models.CharField(max_length=100, null=False, blank=False)
        city = models.CharField(max_length=100, null=False, blank=False)
        state = models.CharField(max_length=2, null=False, blank=False)  
        country = models.CharField(max_length=100, default="Brasil")
        principal = models.BooleanField(default=False)
        slug = models.SlugField(max_length=255, unique=True, editable=False)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.road}, {self.number} - {self.city}/{self.state}"
        
        def get_absolute_url(self):
            return reverse('address-detail', kwargs={'uuid': str(self.id), 'slug': self.slug})
        
        class Meta:
            verbose_name = "Endereço"
            verbose_name_plural =  "Endereços"
            
        def save(self, *args, **kwargs):
            if not self.slug:
                base_slug = slugify(f"{self.road}-{self.number}-{self.district}-{self.city}-{self.state}-{self.country}")
                unique_slug = base_slug
                num = 1
                while User.objects.filter(slug=unique_slug).exists():
                    unique_slug = f'{base_slug}-{num}'
                    num += 1
                self.slug = unique_slug
            super().save(*args, **kwargs)





"""
class Profile(models.Model):
    biografia = models.TextField(blank=True, null=True)
    instagram = models.URLField(max_length=255, null=True, blank=True)
    facebook = models.URLField(max_length=255, null=True, blank=True)
    tiktok = models.URLField(max_length=255, null=True, blank=True)
    whatsapp = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="profile")

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return f"Perfil de {self.user.username}"

@deconstructible
class MediaTypeValidator:
    def __init__(self, media_type):
        self.media_type = media_type

    def __call__(self, value):
        # Verificando o tipo de arquivo para foto ou vídeo
        if self.media_type == "photo":
            # Verifica se o arquivo é uma imagem
            if imghdr.what(value) not in ["jpeg", "png", ".jpg"]:
                raise ValidationError("O arquivo não é uma imagem válida.")
        elif self.media_type == "video":
            # Verifica se o arquivo é um vídeo
            if not value.name.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                raise ValidationError("O arquivo não é um vídeo válido.")

class ProfileMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("photo", "Foto"),
        ("video", "Vídeo"),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="media")
    file_name = models.CharField(max_length=100, blank=False, null=False)
    file = models.FileField(upload_to="profile_media/")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)  # Para marcar a foto/vídeo principal

    # Validação do tipo de arquivo com base no tipo selecionado
    def clean(self):
        # Chama a validação personalizada para garantir que o tipo de arquivo corresponde ao tipo de mídia
        file_validator = MediaTypeValidator(self.media_type)
        file_validator(self.file)

    class Meta:
        verbose_name = "Mídia do Perfil"
        verbose_name_plural = "Mídias dos Perfis"

    def __str__(self):
        return f"{self.media_type.capitalize()} de {self.profile.user.username}"
    

    """