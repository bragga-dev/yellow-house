from pyexpat.errors import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from user.forms import AddressForm
from user.models import ClientAddress, ArtistAddress
from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

from user.forms import AddressForm  # ajuste o import conforme sua estrutura
from user.models import Artist, Client  # supondo que existam esses modelos

logger = logging.getLogger(__name__)

@login_required
def create_address(request):
    user = request.user
    logger.debug(f"create_address called with user={user}")

    # determinar owner e tipo
    if getattr(user, 'is_client', False) and getattr(user, 'client', None):
        owner = user.client
        address_type = 'client'
        dashboard_template = 'account/dashboard_client.html'  # corrige pro caminho real
        dashboard_url_name = 'client:dashboard_client'
    elif getattr(user, 'is_artist', False) and getattr(user, 'artist', None):
        owner = user.artist
        address_type = 'artist'
        dashboard_template = 'account/dashboard_artist.html'
        dashboard_url_name = 'artist:dashboard_artist'
    else:
        messages.error(request, "Seu tipo de usuário não é suportado.")
        return redirect('/')

    form = AddressForm(address_type=address_type)
    if request.method == 'POST':
        try:
            logger.info(f"Creating address for owner: {owner}")
            form = AddressForm(request.POST, address_type=address_type)
            if form.is_valid():
                form.save(owner=owner)
                messages.success(request, "Endereço adicionado com sucesso.")
                if address_type == 'client':
                    return redirect(dashboard_url_name, slug=user.slug, pk=user.pk)
                else:
                    return redirect(dashboard_url_name, slug=user.slug, pk=user.pk)
            else:
                # Form inválido: não redireciona, vai renderizar o dashboard abaixo com o form cheio de erros
                messages.error(request, "Corrija os erros no formulário abaixo.")
        except Exception as e:
            logger.error(f"Error creating address: {e}")
            messages.error(request, f"Erro ao adicionar o endereço: {e}")
            # mantém o form com os dados postados para exibir
            form = AddressForm(request.POST, address_type=address_type)

    # aqui: GET ou form inválido -> renderiza o dashboard correspondente com contextos necessários
    # montar contextos como o dashboard espera
    addresses = owner.addresses.all()

    context = {
        'user': user,
        'form': form,
        'addresses': addresses,
        # tanto artista quanto cliente podem usar essas chaves no template
        'artist': owner if address_type == 'artist' else getattr(user, 'artist', None),
        'client': owner if address_type == 'client' else getattr(user, 'client', None),
    }

    return render(request, dashboard_template, context)



@login_required
def update_address(request, pk):
    logger.debug(f"edit_address called with pk={pk} and user={request.user}")

    address = get_object_or_404(pk=pk)

    # Verifica se o usuário é dono do endereço
    if request.user.is_client and hasattr(request.user, 'client'):
        if address.client != request.user.client:
            messages.error(request, "Você não tem permissão para editar este endereço.")
            return redirect('profile')
        owner = request.user.client
        address_type = 'client'

    elif request.user.is_artist and hasattr(request.user, 'artist'):
        if address.artist != request.user.artist:
            messages.error(request, "Você não tem permissão para editar este endereço.")
            return redirect('profile')
        owner = request.user.artist
        address_type = 'artist'

    else:
        messages.error(request, "Seu tipo de usuário não é suportado.")
        return redirect('home')

    # Formulário
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address, address_type=address_type)
        if form.is_valid():
            form.save(owner=owner)
            messages.success(request, "Endereço atualizado com sucesso.")
            return redirect('profile')
    else:
        form = AddressForm(instance=address, address_type=address_type)

    return render(request, 'account/edit_address.html', {'form': form})


@login_required
def delete_address(request, pk):
    logger.debug(f"delete_address called with pk={pk} and user={request.user}")
    user = request.user
    if getattr(user, 'is_client', False):
        address = get_object_or_404(ClientAddress, pk=pk, client=user.client)
        owner_type = 'client'
    elif getattr(user, 'is_artist', False) and getattr(user, 'artist', None):
        address = get_object_or_404(ArtistAddress, pk=pk, artist=user.artist)
        owner_type = 'artist'
    else:
        messages.error(request, "Seu tipo de usuário não é suportado.")
        return redirect('home')
   
    if request.method == 'POST':
        try:
            logger.info(f"Deleting address: {address}")
            address.delete()
            messages.success(request, "Endereço excluído com sucesso.")
        except Exception as e:
            logger.error(f"Error deleting address: {e}")
            messages.error(request, f"Erro ao excluir o endereço: {e}")
        if owner_type == 'client':
            return redirect('client:dashboard_client', slug=user.slug, pk=user.pk)
        elif owner_type == 'artist':
            return redirect('artist:dashboard_artist', slug=user.slug, pk=user.pk)
    return render(request, 'account/confirm_delete_address.html', {'address': address})
