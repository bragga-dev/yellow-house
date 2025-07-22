
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import ClientAddress, Artist, Client
from user.forms import UserUpdateForm, AddressForm, ClientUpdateForm
from user.models import User


@login_required
def update_profile_client(request, slug, pk):
    user = get_object_or_404(User, slug=slug, pk=pk, is_client=True)
    client = user.client
    address = client.addresses.first() if client.addresses.exists() else None

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        client_form = ClientUpdateForm(request.POST, instance=client)
        address_form = AddressForm(
            request.POST, 
            instance=address, 
            address_type='client'
        )

        if user_form.is_valid() and client_form.is_valid() and address_form.is_valid():
            user_form.save()
            client_form.save()
            address_form.save(owner=client)  # repassando o client
            return redirect('dashboard_client', slug=user.slug, pk=user.pk)# redirecione para onde quiser
    else:
        user_form = UserUpdateForm(instance=user)
        client_form = ClientUpdateForm(instance=client)
        address_form = AddressForm(
            instance=address,
            address_type='client'
        )

    context = {
        'user_form': user_form,
        'client_form': client_form,
        'address_form': address_form,
    }
    return render(request, 'account/update_profile_client.html', context)



@login_required
def request_artist(request):
    client = request.user.client
    if request.method == "POST":
        client.wants_to_be_artist = True
        client.save()
    return redirect('perfil')
