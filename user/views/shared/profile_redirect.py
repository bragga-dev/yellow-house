from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import ClientAddress, Artist, Client
from user.forms import UserUpdateForm, AddressForm, ArtistUpdateForm, ClientUpdateForm
from user.decorators import is_staff_required


@login_required
def profile_redirect(request, slug, pk):
    user = request.user
    if getattr(user, 'is_artist', False):
        return redirect('update_profile_artist', slug=user.slug, pk=user.pk)
    elif getattr(user, 'is_client', False):
        return redirect('dashboard_client', slug=user.slug, pk=user.pk)
    # elif user.is_staff:
    #     return redirect('update_profile_staff', slug=user.slug, pk=user.pk)
    else:
        messages.error(request, "Tipo de usuário não reconhecido.")
        return redirect('/')








@login_required
def address_create_view(request):
    user = request.user
    if user.is_client:
        address_type = 'client'
        instance_owner = user.client
    elif user.is_artist:
        address_type = 'artist'
        instance_owner = user.artist
    else:
        return redirect('home')  # ou mostrar erro

    if request.method == 'POST':
        form = AddressForm(request.POST, address_type=address_type)
        if form.is_valid():
            address = form.save(commit=False)
            if address_type == 'client':
                address.client = instance_owner
            else:
                address.artist = instance_owner
            address.save()
            return redirect('perfil')  # ou para a lista de endereços
    else:
        form = AddressForm(address_type=address_type)

    return render(request, 'enderecos/form_address.html', {'form': form})



@login_required
@is_staff_required
def migrate_client_to_artist(request):
    user = request.user

    if user.is_client and not user.is_artist:
        # Atualiza flags
        user.is_client = False
        user.is_artist = True
        user.save()

        # Remove perfil Client se existir
        if hasattr(user, 'client'):
            user.client.delete()

        # Cria perfil Artist
        if not hasattr(user, 'artist'):
            Artist.objects.create(user=user)

    return redirect('perfil')  # redireciona pra onde você quiser
