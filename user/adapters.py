from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from user.models import Client
import requests
from django.core.files.base import ContentFile
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from user.models import Client
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_client:
            return resolve_url('/')
        elif user.is_artist:
            return resolve_url('/')
        return super().get_login_redirect_url(request)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        Conecta contas sociais a usuários existentes com mesmo email,
        sem quebrar o fluxo normal de login.
        """
        if sociallogin.is_existing:
            return

        if request.user.is_authenticated:
            return

        extra_data = getattr(sociallogin.account, "extra_data", {}) or {}
        email = extra_data.get("email") or getattr(sociallogin.user, "email", None)

        if not email:
            return

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return

        # Verifica se já existe EmailAddress verificado
        try:
            email_record = EmailAddress.objects.get(user=user, email__iexact=email)
            verified_in_system = email_record.verified
        except EmailAddress.DoesNotExist:
            verified_in_system = False

        provider_flag = extra_data.get("email_verified")
        provider_verified = str(provider_flag).lower() in ("true", "1", "yes") if provider_flag is not None else False

        if verified_in_system or provider_verified:
            # Cria registro de email verificado se necessário
            if not verified_in_system and provider_verified:
                EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
            # Conecta a conta social ao usuário existente
            sociallogin.connect(request, user)

    def save_user(self, request, sociallogin, form=None):
        """
        Mantém toda a lógica atual: cria cliente se necessário
        e salva o usuário.
        """
        user = super().save_user(request, sociallogin, form)

        # Definir como cliente se não for artista nem cliente
        if not user.is_client and not user.is_artist:
            user.is_client = True
            user.save()

        # Criar instância de Client se ainda não existir
        if user.is_client and not hasattr(user, 'client'):
            Client.objects.create(user=user)

        # --- Baixar foto do Google apenas se não houver foto ---
        extra_data = getattr(sociallogin.account, 'extra_data', {}) or {}
        picture_url = extra_data.get("picture")
        if picture_url and not user.photo:
            try:
                resp = requests.get(picture_url)
                if resp.status_code == 200:
                    user.photo.save(
                        f"{user.username}_google.jpg",
                        ContentFile(resp.content),
                        save=True
                    )
            except Exception as e:
                print("Erro ao baixar foto do Google:", e)

        return user

