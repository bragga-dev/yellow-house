from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import ClientAddress, Artist, User
from user.forms import UserUpdateForm, AddressForm, AddressUpdateForm, ArtistUpdateForm




@login_required
def update_profile_artist(request, slug, pk):
    user = get_object_or_404(Artist, slug=slug, pk=pk)

    if request.user != user:
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

    return render(request, 'account/update_profile.html', context)

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


