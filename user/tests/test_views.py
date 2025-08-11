from django.test import TestCase, Client as DjangoClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import Client, ClientAddress, Artist, ArtistAddress
from django.contrib.messages import get_messages
from user.models import ClientAddress, Client  
from user.forms import AddressForm
import uuid

import logging
logger = logging.getLogger(__name__)







User = get_user_model()

class AddressViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_client = User.objects.create_user(
            username="Roberto",
            first_name="Test",
            last_name="Dias",
            email="fernado@gmail.com",
            password="testpassword",
            is_client=True
        )
        

        cls.user_artist = User.objects.create_user(
            username="Fulano",
            first_name="Artist",
            last_name="User",
            email="braga@gmail.com",
            password="artistpassword",
            is_artist=True
        )
        cls.client_instance = Client.objects.create(user=cls.user_client)
    
    # Para o artista, pega o que foi criado automaticamente pelo save do User
        cls.artist_instance = cls.user_artist.artist

        cls.address_client = ClientAddress.objects.create(
            client=cls.client_instance,
            road="Rua Teste",
            number="123",
            district="Centro",  
            city="Cidade",
            state="BA",         
            country="País",
            cep="45201-347"
        )
        
        cls.address_artist = ArtistAddress.objects.create(
            artist=cls.artist_instance,
            road="Rua Artista",
            number="456",
            district="Bairro Artista",
            city="Cidade Artista",
            state="SP",
            country="Brasil",
            cep="45201-347"
        )

    def setUp(self):
        self.client = DjangoClient()
        self.artist_client = DjangoClient()
        self.client.force_login(self.__class__.user_client)
        self.artist_client.force_login(self.__class__.user_artist)

    def test_create_address_client_get(self):
        url = reverse('shared:create_address')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/dashboard_client.html')

    def test_create_address_artist_get(self):
        url = reverse('shared:create_address')
        response = self.artist_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/dashboard_artist.html')

    def test_create_address_client_post_valid(self):
        url = reverse('shared:create_address')
        data = {
            'road': "Nova Rua",
            'number': "456",
            'district': "Bairro Novo",
            'city': "Nova Cidade",
            'state': "RJ",
            'country': "Brasil",
            'cep': "45201-347"
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ClientAddress.objects.filter(road="Nova Rua", client=self.__class__.client_instance).exists())
        self.assertRedirects(response, reverse('client:dashboard_client', kwargs={'slug': self.__class__.user_client.slug, 'pk': self.__class__.user_client.pk}))

    def test_create_address_artist_post_valid(self):
        url = reverse('shared:create_address')
        data = {
            'road': "Rua Artista Nova",
            'number': "789",
            'district': "Bairro Artista Novo",
            'city': "Cidade Artista Nova",
            'state': "MG",
            'country': "Brasil",
            'cep': "45201-347"
        }
        response = self.artist_client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ArtistAddress.objects.filter(road="Rua Artista Nova", artist=self.__class__.artist_instance).exists())
        self.assertRedirects(response, reverse('artist:dashboard_artist', kwargs={'slug': self.__class__.user_artist.slug, 'pk': self.__class__.user_artist.pk}))

    def test_create_address_client_post_invalid(self):
        url = reverse('shared:create_address')
        data = {
            'road': "", 
            'number': "456",
            'district': "Bairro Novo",
            'city': "Nova Cidade",
            'state': "RJ",
            'country': "Brasil",
            'cep': "45201-347"
        }
        response = self.client.post(url, data, follow=True)
        print("Errors: ", response.context['form'].errors)
        print("Status code:", response.status_code)
        print("Templates usados:", [t.name for t in response.templates])
        print("Chaves no contexto:", response.context.keys() if response.context else 'Sem contexto')
        print("Erros do formulário:", response.context['form'].errors if response.context and 'form' in response.context else 'Sem form no contexto')
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.has_error('road'))
        self.assertIn('Este campo é obrigatório.', form.errors['road'])
        self.assertTemplateUsed(response, 'account/dashboard_client.html')
        
    def test_update_address_client_get(self):
        url = reverse('shared:update_address', kwargs={'pk': self.__class__.address_client.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/update_address.html')

    def test_delete_address_success(self):
        url = reverse('shared:delete_address', kwargs={'pk': self.__class__.address_client.pk})
        response = self.client.post(url, follow=True)
        self.assertFalse(ClientAddress.objects.filter(pk=self.__class__.address_client.pk).exists())
        self.assertRedirects(response, reverse('client:dashboard_client', kwargs={'slug': self.__class__.user_client.slug, 'pk': self.__class__.user_client.pk}))

    def test_delete_address_not_found(self):
        fake_uuid = uuid.uuid4()  
        url = reverse('shared:delete_address', kwargs={'pk': str(fake_uuid)})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)  

    def test_delete_address_unauthorized(self):
        # Tentar deletar o endereço do cliente logado como artista
        url = reverse('shared:delete_address', kwargs={'pk': self.__class__.address_client.pk})
        response = self.artist_client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ClientAddress.objects.filter(pk=self.__class__.address_client.pk).exists())
        
    def test_delete_address_artist_success(self):
        url = reverse('shared:delete_address', kwargs={'pk': self.__class__.address_artist.pk})
        response = self.artist_client.post(url, follow=True)
        self.assertFalse(ArtistAddress.objects.filter(pk=self.__class__.address_artist.pk).exists())
        self.assertRedirects(response, reverse('artist:dashboard_artist', kwargs={'slug': self.__class__.user_artist.slug, 'pk': self.__class__.user_artist.pk}))
        
    def test_delete_address_artist_not_found(self):
        fake_uuid = uuid.uuid4()  
        url = reverse('shared:delete_address', kwargs={'pk': str(fake_uuid)})
        response = self.artist_client.post(url)
        self.assertEqual(response.status_code, 404)