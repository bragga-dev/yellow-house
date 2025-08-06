from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user.models import Client

@login_required
def dashboard_client(request, slug, pk):
    client = get_object_or_404(Client, user__slug=slug, user__pk=pk)
    if client.user != request.user:
        return redirect('account_login') 
    addresses = client.addresses.all()    
    context = {
        'client': client,
        'addresses': addresses,
        'user': client.user,
    }
    return render(request, 'account/dashboard_client.html', context)
    
