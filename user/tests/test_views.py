from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import Client as ClientModel, ClientAddress
import logging
logger = logging.getLogger(__name__)







from django.contrib.messages import get_messages
from user.models import ClientAddress, Client  # ajuste conforme seus modelos
from user.forms import AddressForm

User = get_user_model()

class CreateAddressViewTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='cliente', password='123456')
        self.client_user.is_client = True
        self.client_user.save()
        self.client_profile = Client.objects.create(user=self.client_user, slug='cliente-slug')
        self.client_user.client = self.client_profile

        self.url = reverse('shared:create_address')

    def test_get_request_renders_form(self):
        self.client.login(username='cliente', password='123456')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/create_address.html')
        self.assertIsInstance(response.context['form'], AddressForm)

    def test_post_valid_data_creates_address(self):
        self.client.login(username='cliente', password='123456')
        data = {
            'cep': '12345678',
            'road': 'Rua Teste',
            'number': '100',
            'district': 'Centro',
            'city': 'Jequié',
            'state': 'BA',
            'country': 'Brasil',
            'principal': True,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(ClientAddress.objects.count(), 1)
        address = ClientAddress.objects.first()
        self.assertEqual(address.road, 'Rua Teste')
        self.assertRedirects(response, reverse('client:dashboard_client', kwargs={'slug': self.client_user.slug, 'pk': self.client_user.pk}))

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username='cliente', password='123456')
        data = {
            'cep': '',  # campo obrigatório vazio
            'road': 'Rua Teste',
            'number': '100',
            'district': 'Centro',
            'city': 'Jequié',
            'state': 'BA',
            'country': 'Brasil',
            'principal': True,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'cep', 'Este campo é obrigatório.')

    def test_user_without_type_redirects(self):
        user = User.objects.create_user(username='sem_tipo', password='123456')
        self.client.login(username='sem_tipo', password='123456')
        response = self.client.get(self.url)
        self.assertRedirects(response, '/')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("não é suportado" in str(m) for m in messages))



User = get_user_model()

class DeleteAddressViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="testpassword",
            is_client=True
        )

        self.client_instance = ClientModel.objects.create(user=self.user)

        self.address = ClientAddress.objects.create(
            client=self.client_instance,
            road="Rua Teste",
            number="123",
            district="Centro",  # obrigatório
            city="Cidade",
            state="BA",          # maiúsculo conforme choices
            country="País",
            cep="00000-000"
        )

        self.client = Client()
        self.client.force_login(self.user)  # <<-- correção aqui

    def test_delete_address_success(self):
        url = reverse('shared:delete_address', kwargs={'pk': self.address.pk})
        response = self.client.post(url, follow=True)  # segue redirecionamento
        print("redirect chain:", response.redirect_chain)  # debug: pra onde foi
        # opcional: inspeciona o usuário e se a página final tem algo esperável
        self.assertFalse(ClientAddress.objects.filter(pk=self.address.pk).exists())
        
