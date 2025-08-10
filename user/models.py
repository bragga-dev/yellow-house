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
from brazilcep import get_address_from_cep, WebService
from brazilcep.exceptions import BrazilCEPException



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
    


import os

def validate_image_file(value):
    valid_extensions = ['jpg', 'jpeg', 'png']
    # Tenta obter o path real do arquivo
    try:
        file_path = value.path
    except ValueError:
        # Se não tiver path (ex: arquivo em memória), pula validação aqui
        return
    except Exception:
        return

    # Verifica se o arquivo existe, se não, pula validação
    if not os.path.exists(file_path):
        return

    file_ext = imghdr.what(file_path)
    if file_ext not in valid_extensions:
        raise ValidationError('Formato de arquivo inválido. Use jpg, jpeg ou png.')


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  #
    username = models.CharField( _('username'), max_length=15, unique=True,
        help_text=_('Required. 15 characters or fewer. Letters, numbers and @/./+/-/_ characters'),
        validators=[validators.RegexValidator(re.compile(r'^[\w.@+-]+$'), _('Enter a valid username.'), _('invalid'))])
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True, help_text=_('Formato: DD/MM/AAAA.'))
    photo = models.ImageField(upload_to="photos/", default="photos/default.jpg", blank=True, null=True, validators=[validate_image_file], help_text=_('Formato de arquivo: jpg, jpeg ou png.'))
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)    
    phone = PhoneNumberField(region="BR", unique=True, null=True, blank=True, help_text='Digite um número com DDD. Ex: +55 11 91234-5678')
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    is_client = models.BooleanField(_('client'),  default=False, help_text=_('Designates whether this user is a client.'))
    is_artist = models.BooleanField(_('artist'), default=False, help_text=_('Designates whether this user is an artist.'))      
    is_staff = models.BooleanField(_('staff status'), default=False,  help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,  help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_trusty = models.BooleanField(_('trusty'), default=False, help_text=_('Designates whether this user has confirmed his account.'))
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'uuid': str(self.id), 'slug': self.slug})
    
    
    def has_name_changed(self):
        """Verifica se o nome do usuário mudou"""
        if not self.id:
            return False
            
        old_user = User.objects.filter(id=self.id).first()
        if not old_user:
            return True
            
        return (old_user.first_name != self.first_name or old_user.last_name != self.last_name)
    
    def clean(self):
        if self.cpf and not CPF(repeated_digits=True).validate(self.cpf):
            raise ValidationError({'cpf': 'CPF inválido'})

        if self.is_artist and self.is_client:
            raise ValidationError("O usuário não pode ser Cliente e Artista ao mesmo tempo")
        
        
    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug or self._state.adding or self.has_name_changed():
            base_slug = slugify(self.get_full_name())
            unique_slug = base_slug
            num = 1
            while User.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

        # Cria perfil de artista automaticamente se marcado
        if self.is_artist and not hasattr(self, 'artist'):
            Artist.objects.create(user=self)

def validar_cep(value):
    cep = value.replace('-', '').strip()
    if len(cep) != 8 or not cep.isdigit():
        raise ValidationError('CEP inválido: formato incorreto.')

    try:
        get_address_from_cep(cep, webservice=WebService.VIACEP)
    except BrazilCEPException:
        raise ValidationError('CEP inválido ou não encontrado.')


class BaseAddress(models.Model):
        class States(models.TextChoices):
            AC = "AC", "Acre"
            AL = "AL", "Alagoas"
            AP = "AP", "Amapá"
            AM = "AM", "Amazonas"
            BA = "BA", "Bahia"
            CE = "CE", "Ceará"
            DF = "DF", "Distrito Federal"
            ES = "ES", "Espírito Santo"
            GO = "GO", "Goiás"
            MA = "MA", "Maranhão"
            MT = "MT", "Mato Grosso"
            MS = "MS", "Mato Grosso do Sul"
            MG = "MG", "Minas Gerais"
            PA = "PA", "Pará"
            PB = "PB", "Paraíba"
            PR = "PR", "Paraná"
            PE = "PE", "Pernambuco"
            PI = "PI", "Piauí"
            RJ = "RJ", "Rio de Janeiro"
            RN = "RN", "Rio Grande do Norte"
            RS = "RS", "Rio Grande do Sul"
            RO = "RO", "Rondônia"
            RR = "RR", "Roraima"
            SC = "SC", "Santa Catarina"
            SP = "SP", "São Paulo"
            SE = "SE", "Sergipe"
            TO = "TO", "Tocantins"


        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        cep = models.CharField(_('CEP'), max_length=9, null=False, blank=False, validators=[validar_cep])  
        road = models.CharField(_('Rua'), max_length=255, null=False, blank=False)
        number = models.CharField(_('N°'), max_length=10, null=False, blank=False)
        district = models.CharField(_('Bairro'), max_length=100, null=False, blank=False)
        city = models.CharField(_('Cidade'), max_length=100, null=False, blank=False)
        state = models.CharField(_('Estado'),  max_length=2, choices=States.choices, null=False,  blank=False)
        country = models.CharField(_('País'), max_length=100, default="Brasil")
        principal = models.BooleanField(_('Endereço Padrão?'), default=True, help_text=_('Define este endereço como o principal para entregas.'))
        slug = models.SlugField(max_length=255, unique=True, editable=False)
        complement = models.CharField(_('Complemento'), max_length=255, null=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"{self.road}, {self.number} - {self.city}/{self.state}"
    

        def get_absolute_url(self):
            return reverse('address-detail', kwargs={'uuid': str(self.id), 'slug': self.slug})
        
        class Meta:
            verbose_name = "Endereço"
            verbose_name_plural =  "Endereços"
            abstract = True
            
        def save(self, *args, **kwargs):
            if not self.slug:
                base_slug = slugify(f"{self.road}-{self.number}-{self.district}-{self.city}-{self.state}-{self.country}")
                unique_slug = base_slug
                num = 1
                while self.__class__.objects.filter(slug=unique_slug).exists():
                    unique_slug = f'{base_slug}-{num}'
                    num += 1
                self.slug = unique_slug
            super().save(*args, **kwargs)


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client")
    wants_to_be_artist = models.BooleanField(_('Quero ser Artista!'), default=False)


    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class ClientAddress(BaseAddress):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='addresses')

    def save(self, *args, **kwargs):
        # Se o endereço atual for definido como principal
        if self.principal:
            # Define todos os outros como não principais
            ClientAddress.objects.filter(client=self.client, principal=True).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)
    


class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="artist")
    is_verified = models.BooleanField(_('Autorizado?'), default=False, help_text="Indica se o artista foi verificado pela plataforma.")
    bio = models.TextField(_('Biografia'), blank=True, null=True, help_text=_('Conte um pouco sobre você.'))


    class Meta:
        verbose_name = "Artista"
        verbose_name_plural = "Artistas"

class ArtistAddress(BaseAddress):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='addresses')

    def save(self, *args, **kwargs):
        # Se o endereço atual for definido como principal
        if self.principal:
            # Define todos os outros como não principais
            ArtistAddress.objects.filter(artist=self.artist, principal=True).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)


    
class Exhibitions(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='exhibitions')
    title = models.CharField(_('Título'), max_length=255)
    description = models.TextField(_('Descrição'), blank=True, null=True)
    date = models.DateField(_('Data'), null=False, blank=False)
    location = models.CharField(_('Localização'), max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)