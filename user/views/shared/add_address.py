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
    logger.debug(f"update_address called with pk={pk} and user={request.user}")
    user = request.user

    if getattr(user, 'is_client', False) and getattr(user, 'client', None):
        owner = user.client
        address = get_object_or_404(ClientAddress, pk=pk, client=owner)
        owner_type = 'client'
        dashboard_template = 'account/dashboard_client.html'
        dashboard_url_name = 'client:dashboard_client'
    elif getattr(user, 'is_artist', False) and getattr(user, 'artist', None):
        owner = user.artist
        address = get_object_or_404(ArtistAddress, pk=pk, artist=owner)
        owner_type = 'artist'
        dashboard_template = 'account/dashboard_artist.html'
        dashboard_url_name = 'artist:dashboard_artist'
    else:
        messages.error(request, "Seu tipo de usuário não é suportado.")
        return redirect('/')

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address, address_type=owner_type)
        if form.is_valid():
            try:
                form.save(owner=owner)
                messages.success(request, "Endereço atualizado com sucesso.")
                return redirect(dashboard_url_name, slug=user.slug, pk=user.pk)
            except Exception as e:
                logger.error(f"Erro ao salvar endereço: {e}")
                messages.error(request, f"Erro ao atualizar o endereço: {e}")
        else:
            # Form inválido — reconstruir dashboard e reabrir modal
            messages.error(request, "Corrija os erros no formulário.")

            # Buscar todos os endereços
            addresses = list(owner.addresses.all())

            # Anexar o edit_form correto a cada endereço
            for addr in addresses:
                if addr.pk == address.pk:
                    # O endereço com erro recebe o form com erros
                    addr.edit_form = form
                    addr.open_modal = True  # flag para template reabrir o modal
                else:
                    addr.edit_form = AddressForm(instance=addr, address_type=owner_type)

            context = {
                'user': user,
                'addresses': addresses,
                'form': AddressForm(address_type=owner_type),  # form de criação
                'artist': owner if owner_type == 'artist' else getattr(user, 'artist', None),
                'client': owner if owner_type == 'client' else getattr(user, 'client', None),
            }
            return render(request, dashboard_template, context)

    # GET (ex: carregando modal pela primeira vez)
    form = AddressForm(instance=address, address_type=owner_type)
    return render(request, 'account/update_address.html', {'form': form, 'address': address})

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
