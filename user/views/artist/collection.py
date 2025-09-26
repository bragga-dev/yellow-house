from user.forms import ExhibitionForm
from user.models import Exhibitions, Artist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404




@login_required
def collection(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
   
    
    context = {
        'artist': artist
    }
        
    return render(request, 'account/collection.html', context)