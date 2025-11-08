from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from vitrine.forms import ArtWorkForm, PackageForm
from vitrine.models import ArtWork, ArtworkImage, ArtworkCategory
from vitrine.filters import ArtWorkFilter
from django.core.paginator import Paginator
from django.http import JsonResponse
from vitrine.models import ArtWork
from vitrine.services.frenet import calcular_frete
from vitrine.utils import calcular_frete_item

@login_required
def create_artwork(request):
    if not getattr(request.user, 'is_artist', False) or not hasattr(request.user, 'artist'):
        messages.error(request, "Somente artistas podem criar obras.")
        return redirect('account_login')

    artist = request.user.artist

    if request.method == 'POST':
        form_artwork = ArtWorkForm(request.POST, request.FILES)
        form_package = PackageForm(request.POST)
        form_artwork.fields['art_work_category'].queryset = ArtworkCategory.objects.all()

        images = request.FILES.getlist("images")
        primary_index = int(request.POST.get("is_primary", 0))  

        if form_artwork.is_valid() and form_package.is_valid():
            package = form_package.save()

            artwork = form_artwork.save(commit=False)
            artwork.artist = artist
            artwork.package = package
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
            'form_package': form_package
        })

    return redirect('artist:collection', slug=request.user.slug, pk=request.user.pk)


@login_required
def update_artwork(request, slug, artwork_id):
    
    artwork = get_object_or_404(ArtWork, slug=slug, id=artwork_id, artist__user=request.user)
    artist = request.user.artist

    if request.method == 'POST':
        form_package = PackageForm(request.POST, instance=artwork.package)
        form_artwork = ArtWorkForm(request.POST, request.FILES, instance=artwork)
        form_artwork.fields['art_work_category'].queryset = ArtworkCategory.objects.all()

        images = request.FILES.getlist("images")
        primary_index = int(request.POST.get("is_primary", 0)) if request.POST.get("is_primary") else 0

        if form_artwork.is_valid() and form_package.is_valid():
            packege = form_package.save()

            updated_artwork = form_artwork.save(commit=False)
            updated_artwork.artist = artist
            updated_artwork.package = packege
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
            'form_package': form_package
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
    artworks = ArtWork.objects.filter(artist__user__slug=slug, artist__user__pk=pk, stock__gt=0).all().order_by('-created_at')

    pagination = Paginator(artworks, 8)
    page_number = request.GET.get('page')
    artworks = pagination.get_page(page_number)  

    return render(request, 'vitrine/artist_detail.html', {'artworks': artworks})



# def detail_artwork(request, slug, artwork_id):
#     artwork = get_object_or_404(ArtWork, slug=slug, id=artwork_id)
#     resultado_frete = None
#     resultado_frete_valido = []

#     if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
#         endereco_principal = artwork.artist.addresses.filter(principal=True).first()
#         if not endereco_principal:
#             return JsonResponse({"error": "O artista não possui um endereço principal cadastrado."})

#         cep_origem = endereco_principal.cep
#         cep_destino = request.POST.get("cep_destino")
#         quantidade = int(request.POST.get("quantidade", 1))

#         package = artwork.package
#         if not package:
#             return JsonResponse({"error": "Nenhuma embalagem cadastrada para esta obra."})

#         peso_total = package.weight * quantidade
#         valor_total = float(artwork.price) * quantidade

#         resultado_frete = calcular_frete(
#             origem_cep=cep_origem,
#             destino_cep=cep_destino,
#             peso=peso_total,
#             altura=package.height,
#             largura=package.width,
#             comprimento=package.length,
#             valor=valor_total
#         )

#         resultado_frete_valido = [
#             s for s in resultado_frete.get("ShippingSevicesArray", [])
#             if not s.get("Error", True)
#         ]

#         return JsonResponse({"fretes": resultado_frete_valido})

#     context = {
#         "artwork": artwork,
#     }
#     return render(request, "vitrine/artwork_detail.html", context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from vitrine.utils import calcular_frete_item  # ajuste conforme o caminho real

def detail_artwork(request, slug, artwork_id):
    artwork = get_object_or_404(ArtWork, slug=slug, id=artwork_id)

    # Se for uma requisição AJAX para cálculo de frete
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        cep_destino = request.POST.get("cep_destino")
        try:
            quantidade = int(request.POST.get("quantity", 1))
        except ValueError:
            return JsonResponse({"error": "Quantidade inválida."}, status=400)

        endereco_origem = artwork.artist.addresses.filter(principal=True).first()
        if not endereco_origem:
            return JsonResponse({"error": "O artista não possui endereço principal cadastrado."}, status=400)

        if not cep_destino:
            return JsonResponse({"error": "CEP de destino não informado."}, status=400)

        if not artwork.package:
            return JsonResponse({"error": "Nenhuma embalagem cadastrada para esta obra."}, status=400)

        resultado = calcular_frete_item(
            origem_cep=endereco_origem.cep,
            destino_cep=cep_destino,
            package=artwork.package,
            valor_unitario=artwork.price,
            quantidade=quantidade
        )

        if "error" in resultado:
            return JsonResponse({"error": resultado["error"]}, status=500)

        return JsonResponse({"fretes": resultado["fretes"]})

    # Renderização normal da página
    return render(request, "vitrine/artwork_detail.html", {"artwork": artwork})

def list_artworks(request):
    artworks = ArtWork.objects.filter(stock__gt=0, package__isnull=False).order_by('-created_at')
    artwork_filter = ArtWorkFilter(request.GET, queryset=artworks)
    filtered_qs = artwork_filter.qs  
    
    pagination = Paginator(filtered_qs, 8)
    page_number = request.GET.get('page')
    artworks_page = pagination.get_page(page_number)

    return render(request, 'vitrine/list_artworks.html', {
        'filter': artwork_filter,
        'artworks': artworks_page,  
        'art_work_categories': ArtworkCategory.objects.all(),
        'styles': ArtWork.objects.values_list('style', flat=True)
                                 .distinct()
                                 .exclude(style__isnull=True)
                                 .exclude(style=''),
    })
