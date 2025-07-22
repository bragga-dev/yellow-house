from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user.models import Client, User

@login_required
def dashboard_client(request, slug, pk):
    user = get_object_or_404(User, slug=slug, pk=pk, is_client=True)
    client = user.client
    addresses = client.addresses.all()  # acessa ClientAddress via related_name

    context = {
        'client': client,
        'addresses': addresses,
    }
    print(context)  # Debugging line to check context data

    return render(request, 'account/dashboard_client.html', context)
