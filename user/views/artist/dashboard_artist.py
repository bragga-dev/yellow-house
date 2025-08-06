from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user.models import Artist
from user.forms import AddressForm

@login_required
def dashboard_artist(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    if artist.user != request.user:
        return redirect('account_login') 
    addresses = artist.addresses.all()    
    form = AddressForm(address_type='artist')  # instância vazia pra povoar o modal

    context = {
        'artist': artist,
        'addresses': addresses,
        'user': artist.user,
        'form': form,  # importante: fornece o form pro include do modal
    }
    return render(request, 'account/dashboard_artist.html', context)

