from django.shortcuts import render, redirect, get_object_or_404
from vitrine.models import Souvenir, SouvenirCategory
from vitrine.filters import SouvenirFilter
from django.core.paginator import Paginator



def souvenir_detail(request, slug, souvenir_id):
    souvenir = get_object_or_404(Souvenir, slug=slug, id=souvenir_id)
    return render(request, 'vitrine/souvenir_detail.html', {'souvenir': souvenir})


def list_souvenirs(request):
    queryset = Souvenir.objects.filter(stock__gt=0).order_by('-created_at')


    souvenir_filter = SouvenirFilter(request.GET, queryset=queryset)
    filtered_qs = souvenir_filter.qs


    pagination = Paginator(filtered_qs, 8)
    page_number = request.GET.get('page')
    souvenirs_page = pagination.get_page(page_number)

    return render(request, 'vitrine/list_souvenirs.html', {
        'filter': souvenir_filter,
        'souvenirs': souvenirs_page,
        'souvenir_categories': SouvenirCategory.objects.all(),
    })
