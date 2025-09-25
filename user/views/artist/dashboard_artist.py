from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user.models import Artist
from user.forms import AddressForm, DemoteToClientForm

@login_required
def dashboard_artist(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    if artist.user != request.user:
        return redirect('account_login')

    # transformar em lista para podermos adicionar atributos nos objetos
    addresses = list(artist.addresses.all().order_by('id'))

    # formulário usado para criar novo endereço (modal de criação)
    form = AddressForm(address_type='artist')

    # anexar um edit_form em cada endereço (instância já preenchida com instance=addr)
    for addr in addresses:
        addr.edit_form = AddressForm(instance=addr, address_type='artist')
    demote_form = DemoteToClientForm()

    context = {
        'artist': artist,
        'addresses': addresses,
        'user': artist.user,
        'form': form,
        'demote_form': demote_form,
    }
    return render(request, 'account/dashboard_artist.html', context)
