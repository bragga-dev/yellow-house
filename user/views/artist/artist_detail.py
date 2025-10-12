from django.shortcuts import render, get_object_or_404
from user.models import Artist, ArtistAddress
from django.db.models import Q
import re

def artist_detail(request, slug, pk, limit=10):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    principal_address = ArtistAddress.objects.filter(artist=artist, principal=True).first()

    query = Q()
    if principal_address:
        query |= Q(addresses__city=principal_address.city)   
        
        

    keywords = re.findall(r'\w{3,}', artist.bio or '')
    for word in keywords:
        query |= Q(bio__icontains=word)

    artists = Artist.objects.filter(is_verified=True).filter(query).exclude(id=artist.id).distinct().order_by('user__username')[:limit]

    context = {
        'artist': artist,
        'artists': artists,
    }
    return render(request, 'account/artist_detail.html', context)
