from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import ClientAddress, Artist, Client
from user.forms import UserUpdateForm, AddressForm, AddressUpdateForm, ArtistUpdateForm, ClientUpdateForm
from user.decorators import is_staff_required


@login_required
def update_profile_redirect(request, slug, pk):
    user = request.user
    print(f"Autenticado: {user.is_authenticated}")
    print(f"User: {user}, slug: {user.slug}, pk: {user.pk}")
    print(f"is_client: {getattr(user, 'is_client', 'N/A')}, is_artist: {getattr(user, 'is_artist', 'N/A')}")

    if getattr(user, 'is_artist', False):
        return redirect('update_profile_artist', slug=user.slug, pk=user.pk)
    elif getattr(user, 'is_client', False):
        return redirect('update_profile_client', slug=user.slug, pk=user.pk)
    else:
        messages.error(request, "Tipo de usuário não reconhecido.")
        return redirect('/')


@login_required
def update_profile_artist(request, slug, pk):
    user = get_object_or_404(Artist, user__slug=slug, user__pk=pk)

    if request.user != user.user:
        messages.error(request, 'Você não tem permissão para editar este perfil.')
        return redirect('/')  # substitua por '/' se preferir

    if request.method == 'POST':
        form = ArtistUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('/')  
    else:
        form = ArtistUpdateForm(instance=user)

    context = {
        'form': form,
        'user': user,
    }

    return render(request, 'account/update_profile_artist.html', context)



@login_required
def update_profile_client(request, slug, pk):
    user = get_object_or_404(Client, user__slug=slug, user__pk=pk)    

    if request.user != user.user:
        messages.error(request, 'Você não tem permissão para editar este perfil.')
        return redirect('/')  # substitua por '/' se preferir

    if request.method == 'POST':
        form = ClientUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('/')  
    else:
        form = ClientUpdateForm(instance=user)

    context = {
        'form': form,
        'user': user,
    }

    return render(request, 'account/update_profile_client.html', context)

# Endereço
@login_required
def create_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('/')
    else:
        form = AddressForm()    
    return render(request, 'account/create_address.html', {'form': form})

@login_required
def update_address(request, slug, pk):
    address = get_object_or_404(ClientAddress, slug=slug, pk=pk)
    if request.method == 'POST':
        if request.user != address.user:
            messages.error(request, 'Você não tem permissão para editar este endereço.')
            return redirect('/')
        form = AddressUpdateForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = AddressForm(instance=address)
    return render(request, 'account/update_address.html', {'form': form})


@login_required
def request_artist(request):
    client = request.user.client
    if request.method == "POST":
        client.wants_to_be_artist = True
        client.save()
    return redirect('perfil')


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
