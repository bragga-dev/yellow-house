from django.shortcuts import render
from vitrine.models import BannerGroup, ArtWork, Souvenir
from django.core.paginator import Paginator
from django.db.models import Q
from user.models import Artist
from vitrine.forms import SearchForm

def index(request):
    group = BannerGroup.objects.filter(is_active=True).first()
    banners = group.images.all().order_by('-is_primary') if group else []

    context = {
        'group': group,
        'banners': banners
    }
    return render(request, "vitrine/index.html", context)


def artworks_partial(request):
    page_number = request.GET.get('page', 1)
    artworks_list = ArtWork.objects.filter(package__isnull=False).order_by('-id')
    paginator = Paginator(artworks_list, 16)
    artworks = paginator.get_page(page_number)
    context = {
        'artworks': artworks
    }
    return render(request, "partials/_artworks.html", context)

def souvenirs_partial(request):
    page_number = request.GET.get('page', 1)
    souvenirs_list = Souvenir.objects.filter(package__isnull=False).order_by('-id')
    paginator = Paginator(souvenirs_list, 16)
    souvenirs = paginator.get_page(page_number)
    context = {
        'souvenirs': souvenirs
    }   
    return render(request, "partials/_souvenirs.html", context)





def search_results(request):
    form = SearchForm(request.GET or None)
    query = None
    artworks = []
    souvenirs = []
    artists = []

    if form.is_valid() and form.cleaned_data.get('query'):
        query = form.cleaned_data['query']

        artworks = ArtWork.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(art_work_category__name__icontains=query)
        )

        souvenirs = Souvenir.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(souvenir_category__name__icontains=query)
        )

        artists = Artist.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(bio__icontains=query)
        )


    context = {
        'form': form,
        'query': query,
        'artworks': artworks,
        'souvenirs': souvenirs,
        'artists': artists,
    }

    return render(request, 'vitrine/search_results.html', context)
