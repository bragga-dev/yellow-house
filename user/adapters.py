from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from user.models import Client



class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_client:
            return resolve_url('/')
        elif user.is_artist:
            return resolve_url('/')
        return super().get_login_redirect_url(request)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Definir como cliente se não for artista nem cliente
        if not user.is_client and not user.is_artist:
            user.is_client = True
            user.save()

        # Criar instância de Client se ainda não existir
        if user.is_client and not hasattr(user, 'client'):
            Client.objects.create(user=user)

        return user
