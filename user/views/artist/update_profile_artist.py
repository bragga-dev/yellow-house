from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import ClientAddress, Artist, User
from user.forms import UserUpdateForm, AddressForm, ArtistUpdateForm, ClientUpdateForm
from user.decorators import is_staff_required





@login_required
def update_profile_artist(request, slug, pk):
    user = get_object_or_404(User, slug=slug, pk=pk, is_artist=True)
    artist = user.artist
    address = artist.addresses.first() if artist.addresses.exists() else None

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        artist_form = ArtistUpdateForm(request.POST, instance=artist)
        address_form = AddressForm(
            request.POST, 
            instance=address, 
            address_type='artist'
        )

        if user_form.is_valid() and artist_form.is_valid() and address_form.is_valid():
            user_form.save()
            artist_form.save()
            address_form.save(owner=artist)  
            return redirect('/')# redirecione para onde quiser
    else:
        user_form = UserUpdateForm(instance=user)
        artist_form = ArtistUpdateForm(instance=artist, user=request.user)
        address_form = AddressForm(
            instance=address,
            address_type='artist'
        )

    context = {
        'user_form': user_form,
        'artist_form': artist_form,
        'address_form': address_form,
    }
    return render(request, 'account/update_profile_artist.html', context)
