from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from vitrine.forms import ArtWorkForm
from vitrine.models import ArtWork, ArtworkImage, ArtworkCategory
from vitrine.filters import ArtWorkFilter
from django.core.paginator import Paginator

@login_required
def create_artwork(request):
    if not getattr(request.user, 'is_artist', False) or not hasattr(request.user, 'artist'):
        messages.error(request, "Somente artistas podem criar obras.")
        return redirect('account_login')

    artist = request.user.artist

    if request.method == 'POST':
        form_artwork = ArtWorkForm(request.POST, request.FILES)
        form_artwork.fields['art_work_category'].queryset = ArtworkCategory.objects.all()

        images = request.FILES.getlist("images")
        primary_index = int(request.POST.get("is_primary", 0))  

        if form_artwork.is_valid():
            artwork = form_artwork.save(commit=False)
            artwork.artist = artist
            artwork.save()

            for i, image_file in enumerate(images):
                is_primary = (i == primary_index)
                ArtworkImage.objects.create(
                    artwork=artwork,
                    image=image_file,
                    is_primary=is_primary
                )

            messages.success(request, 'Obra criada com sucesso!')
            return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

        
        artworks = list(artist.artworks.all().order_by('id'))
        for artwork_obj in artworks:
            artwork_obj.edit_form = ArtWorkForm(instance=artwork_obj)

        return render(request, 'account/collection.html', {
            'artist': artist,
            'artworks': artworks,
            'form_artwork': form_artwork,
        })

    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)


@login_required
def update_artwork(request, slug, artwork_id):
    
    artwork = get_object_or_404(ArtWork, slug=slug, id=artwork_id, artist__user=request.user)
    artist = request.user.artist

    if request.method == 'POST':
        form_artwork = ArtWorkForm(request.POST, request.FILES, instance=artwork)
        form_artwork.fields['art_work_category'].queryset = ArtworkCategory.objects.all()

        images = request.FILES.getlist("images")
        primary_index = int(request.POST.get("is_primary", 0)) if request.POST.get("is_primary") else 0

        if form_artwork.is_valid():
            updated_artwork = form_artwork.save(commit=False)
            updated_artwork.artist = artist
            updated_artwork.save()

           
            if images:
    
                artwork.images.all().delete()

                for i, image_file in enumerate(images):
                    is_primary = (i == primary_index)
                    ArtworkImage.objects.create(
                        artwork=updated_artwork,
                        image=image_file,
                        is_primary=is_primary
                    )
            else:
               
                selected_primary_index = int(request.POST.get("is_primary", 0))
                images_qs = artwork.images.all().order_by('id')  # garantir a ordem correta
                for i, img in enumerate(images_qs):
                    img.is_primary = (i == selected_primary_index)
                    img.save()


            messages.success(request, 'Obra atualizada com sucesso!')
            return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

        
        messages.error(request, 'Por favor, corrija os erros abaixo.')

        artworks = list(artist.artworks.all().order_by('id'))
        for ex in artworks:
            ex.edit_form = form_artwork if ex.id == artwork.id else ArtWorkForm(instance=ex)

        return render(request, 'account/collection.html', {
            'artist': artist,
            'artworks': artworks,
            'form_artwork': ArtWorkForm(), 
        })

    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

@login_required
def delete_artwork(request, slug, artwork_id):
    artwork = get_object_or_404(ArtWork,  slug=slug,  id=artwork_id,  artist=request.user.artist)

    if request.method == 'POST':
        artwork.delete()
        messages.success(request, 'Obra deletada com sucesso!')
        return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)

    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)



def list_artworks_by_artist(request, slug, pk):
    artworks = ArtWork.objects.filter(artist__user__slug=slug, artist__user__pk=pk).all().order_by('-created_at')

    pagination = Paginator(artworks, 8)
    page_number = request.GET.get('page')
    artworks = pagination.get_page(page_number)  

    return render(request, 'vitrine/artist_detail.html', {'artworks': artworks})


def detail_artwork(request, slug, artwork_id):
    artwork = get_object_or_404(ArtWork, slug=slug, id=artwork_id)
    return render(request, 'vitrine/artwork_detail.html', {'artwork': artwork})


def list_artworks(request):
    artworks = ArtWork.objects.all().order_by('-created_at')

    pagination = Paginator(artworks, 8)
    page_number = request.GET.get('page')
    artworks = pagination.get_page(page_number) 
    
    artwork_filter = ArtWorkFilter(request.GET, queryset=artworks)
    
    
    return render(request, 'vitrine/list_artworks.html', {
        'filter': artwork_filter,
        'artworks': artwork_filter.qs,
        'art_work_categories': ArtworkCategory.objects.all(),  
        'styles': ArtWork.objects.values_list('style', flat=True).distinct().exclude(style__isnull=True).exclude(style=''),  
    })