# collection.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from user.forms import ExhibitionForm
from user.models import Exhibitions, Artist
from vitrine.models import ArtWork, ArtworkCategory
from vitrine.forms import ArtWorkForm, PackageForm
from django.core.paginator import Paginator
from django.http import JsonResponse


@login_required
def collection(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    if artist.user != request.user:
        return redirect('account_login')

    form_exhibition = ExhibitionForm()
    form_artwork = ArtWorkForm()
    form_package = PackageForm()

    form_artwork.fields['art_work_category'].queryset = ArtworkCategory.objects.all()

    context = {
        'artist': artist,
        'form_exhibition': form_exhibition,
        'form_artwork': form_artwork,
        'form_package': form_package
    }
    return render(request, 'account/collection.html', context)


@login_required
def create_exhibition(request):
    if not getattr(request.user, 'is_artist', False) or not hasattr(request.user, 'artist'):
        messages.error(request, "Somente artistas podem criar exposições.")
        return redirect('account_login')

    if request.method == 'POST':
        form_exhibition = ExhibitionForm(request.POST, request.FILES)
        if form_exhibition.is_valid():
            exhibition = form_exhibition.save(commit=False)
            exhibition.artist = request.user.artist  
            exhibition.save()
            messages.success(request, 'Exposição criada com sucesso!')
            return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)
        artist = request.user.artist
        exhibitions = list(artist.exhibitions.all().order_by('id'))
        for exhibition in exhibitions:
            exhibition.edit_form = ExhibitionForm(instance=exhibition)

        return render(request, 'account/collection.html', {
            'artist': artist,
            'exhibitions': exhibitions,
            'form_exhibition': form_exhibition,  
        })

    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)


@login_required
def update_exhibition(request, slug, exhibition_id):
    exhibition = get_object_or_404(Exhibitions, slug=slug, id=exhibition_id)

    if exhibition.artist.user != request.user:
        messages.error(request, "Você não tem permissão para editar esta exposição.")
        return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

    if request.method == 'POST':
        form = ExhibitionForm(request.POST, request.FILES, instance=exhibition)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exposição atualizada com sucesso!')
            return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')

         
            artist = request.user.artist
            exhibitions = list(artist.exhibitions.all().order_by('id'))

            for ex in exhibitions:
                ex.edit_form = form if ex.id == exhibition.id else ExhibitionForm(instance=ex)

            return render(request, 'account/collection.html', {
                'artist': artist,
                'exhibitions': exhibitions,
                'form_exhibition': ExhibitionForm(),  
            })

   
    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

@login_required
def delete_exhibition(request, slug, exhibition_id):
    exhibition = get_object_or_404(Exhibitions, slug=slug, id=exhibition_id)

    if exhibition.artist.user != request.user:
        messages.error(request, "Você não tem permissão para deletar esta exposição.")
        return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

    if request.method == 'POST':
        exhibition.delete()
        messages.success(request, 'Exposição deletada com sucesso!')
        return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)




def exhibition_detail(request, slug, exhibition_id):
    exhibition = get_object_or_404(Exhibitions, slug=slug, id=exhibition_id)
    return render(request, 'account/exhibition_detail.html', {'exhibition': exhibition})    


@login_required
def exhibitions_partial(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    if artist.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    exhibitions = artist.exhibitions.all().order_by('-id')
    paginator = Paginator(exhibitions, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for exhibition in page_obj:
        exhibition.edit_form = ExhibitionForm(instance=exhibition)

    return render(request, 'account/partials/exhibitions_list.html', {
        'exhibitions': page_obj,
        'artist': artist
    })


@login_required
def artworks_partial(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    if artist.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    artworks = artist.artworks.all().order_by('-id')
    paginator = Paginator(artworks, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

   
    for artwork in page_obj:
        artwork.edit_form = ArtWorkForm(instance=artwork)

        
        try:
            artwork.package = artwork.package  
        except:
            artwork.package = None

    return render(request, 'account/partials/artworks_list.html', {
        'artworks': page_obj,
        'artist': artist
    })
