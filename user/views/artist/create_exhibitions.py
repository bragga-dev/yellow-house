from user.forms import ExhibitionForm
from user.models import Exhibitions
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages




def create_exhibitions(request):
    if request.method == 'POST':
        form = ExhibitionForm(request.POST, request.FILES)
        if form.is_valid():
            exhibition = form.save(commit=False)
            exhibition.artist = request.user.artist  
            exhibition.save()
            messages.success(request, 'Exhibition created successfully!')
            return redirect('artist:dashboard_artist')  
    else:
        form = ExhibitionForm()
    
    return render(request, 'account/create_exhibitions.html', {'form': form})