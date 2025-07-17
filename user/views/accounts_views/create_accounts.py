from user.forms import ClientSignupForm, ArtistSignupForm
from allauth.account.views import SignupView



class ClientSignupView(SignupView):
    form_class = ClientSignupForm
    template_name = 'account/signup_client.html'


class ArtistSignupView(SignupView):
    form_class = ArtistSignupForm
    template_name = 'account/signup_artist.html'
    