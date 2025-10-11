# collection.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from user.forms import ExhibitionForm
from user.models import Exhibitions, Artist
from vitrine.models import ArtWork
from vitrine.forms import ArtWorkForm


@login_required
def collection(request, slug, pk):
    artist = get_object_or_404(Artist, user__slug=slug, user__pk=pk)
    if artist.user != request.user:
        return redirect('account_login')

    exhibitions = list(artist.exhibitions.all().order_by('id'))
    artworks = list(artist.artworks.all().order_by('id'))

    form_exhibition = ExhibitionForm()
    form_artwork = ArtWorkForm()


    for artwork in artworks:
        artwork.edit_form = ArtWorkForm(instance=artwork)

    for exhibition in exhibitions:
        exhibition.edit_form = ExhibitionForm(instance=exhibition)

    context = {
        'artist': artist,
        'exhibitions': exhibitions,
        'form_exhibition': form_exhibition,
        'artworks': artworks,
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
                'form_exhibition': ExhibitionForm(),  # para modal de criação
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



