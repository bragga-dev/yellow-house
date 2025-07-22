from pyexpat.errors import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from user.forms import AddressForm
from user.models import ClientAddress, ArtistAddress

@login_required
def add_address(request):
    user = request.user

    # Descobre o tipo de endereço baseado no tipo de usuário
    if user.is_client and hasattr(user, 'client'):
        owner = user.client
        address_type = 'client'
    elif user.is_artist and hasattr(user, 'artist'):
        owner = user.artist
        address_type = 'artist'
    else:
        messages.error(request, "Seu tipo de usuário não é suportado.")
        return redirect('home')  # ou outra página de fallback

    # Processamento do formulário
    if request.method == 'POST':
        form = AddressForm(request.POST, address_type=address_type)
        if form.is_valid():
            form.save(owner=owner)
            messages.success(request, "Endereço adicionado com sucesso.")
            return redirect('profile')  # ou a página desejada
    else:
        form = AddressForm(address_type=address_type)

    return render(request, 'account/add_address.html', {
        'form': form,
    })
