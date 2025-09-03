from django.shortcuts import render, redirect, get_object_or_404
from user.models import Artist






def artist_detail(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    context = {
        'artist': artist        
    }
    return render(request, 'account/artist_detail.html', context)