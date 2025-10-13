from django.shortcuts import render, redirect, get_object_or_404
from vitrine.models import Souvenir, SouvenirCategory
from vitrine.filters import SouvenirFilter




def souvenir_detail(request, slug, souvenir_id):
    souvenir = get_object_or_404(Souvenir, slug=slug, id=souvenir_id)
    return render(request, 'vitrine/souvenir_detail.html', {'souvenir': souvenir})


def list_souvenirs(request):
    queryset = Souvenir.objects.all().order_by('-created_at')
    souvenir_filter = SouvenirFilter(request.GET, queryset=queryset)

    return render(request, 'vitrine/list_souvenirs.html', {
        'filter': souvenir_filter,
        'souvenirs': souvenir_filter.qs,
        'souvenir_categories': SouvenirCategory.objects.all(),
    })
