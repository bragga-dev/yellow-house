from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_client:
            return resolve_url('/')
        elif user.is_artist:
            return resolve_url('/')
        return super().get_login_redirect_url(request)
