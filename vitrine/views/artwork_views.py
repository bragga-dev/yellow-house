from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from vitrine.forms import ArtWorkForm
from vitrine.models import ArtWork, ArtworkImage, ArtworkCategory

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
        primary_index = int(request.POST.get("is_primary", 0))  # Índice da imagem principal

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

        # Formulário inválido → renderiza collection com erros
        artworks = list(artist.artworks.all().order_by('id'))
        for artwork_obj in artworks:
            artwork_obj.edit_form = ArtWorkForm(instance=artwork_obj)

        return render(request, 'account/collection.html', {
            'artist': artist,
            'artworks': artworks,
            'form_artwork': form_artwork,
        })

    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)
