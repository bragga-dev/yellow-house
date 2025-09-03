from django.shortcuts import render, get_object_or_404
from user.models import Artist  
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger    

def artists_list(request):
    artists = Artist.objects.all().order_by('user__username')
    page = request.GET.get('page', 1)
    paginator = Paginator(artists, 10)  
    try:
        artists_page = paginator.page(page)
    except PageNotAnInteger:
        artists_page = paginator.page(1)
    except EmptyPage:
        artists_page = paginator.page(paginator.num_pages)

    context = {
        'artists': artists_page
    }
    return render(request, 'account/artists_list.html', context)