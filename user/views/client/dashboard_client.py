from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user.models import Client
from user.forms import AddressForm

@login_required
def dashboard_client(request, slug, pk):
    client = get_object_or_404(Client, user__slug=slug, user__pk=pk)
    if client.user != request.user:
        return redirect('account_login')

    # transformar em lista para podermos adicionar atributos nos objetos
    addresses = list(client.addresses.all().order_by('id'))

    # formulário usado para criar novo endereço (modal de criação)
    form = AddressForm(address_type='client')

    # anexar um edit_form em cada endereço (instância já preenchida com instance=addr)
    for addr in addresses:
        addr.edit_form = AddressForm(instance=addr, address_type='client')

    context = {
        'client': client,
        'addresses': addresses,
        'user': client.user,
        'form': form,
        # não precisa mais enviar edit_forms separado
    }
    return render(request, 'account/dashboard_client.html', context)
