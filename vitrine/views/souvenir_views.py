from django.shortcuts import render, redirect, get_object_or_404
from vitrine.models import Souvenir, SouvenirCategory
from vitrine.filters import SouvenirFilter
from django.core.paginator import Paginator
from django.http import JsonResponse
from vitrine.utils import calcular_frete_item




def souvenir_detail(request, slug, souvenir_id):
    souvenir = get_object_or_404(Souvenir, slug=slug, id=souvenir_id)
    
   
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        cep_destino = request.POST.get("cep_destino")
        try:
            quantidade = int(request.POST.get("quantity", 1))
        except ValueError:
            return JsonResponse({"error": "Quantidade inválida."}, status=400)

        endereco_origem = souvenir.default_address
        if not endereco_origem:
            return JsonResponse({"error": "O artista não possui endereço principal cadastrado."}, status=400)

        if not cep_destino:
            return JsonResponse({"error": "CEP de destino não informado."}, status=400)

        if not souvenir.package:
            return JsonResponse({"error": "Nenhuma embalagem cadastrada para este souvenir."}, status=400)

        resultado = calcular_frete_item(
            origem_cep=endereco_origem.cep,
            destino_cep=cep_destino,
            package=souvenir.package,
            valor_unitario=souvenir.price,
            quantidade=quantidade
        )

        if "error" in resultado:
            return JsonResponse({"error": resultado["error"]}, status=500)
        print("=== FRETES CALCULADOS ===")
        print(resultado["fretes"])
        print("==========================")
        return JsonResponse({"fretes": resultado["fretes"]})   
       
    return render(request, 'vitrine/souvenir_detail.html', {'souvenir': souvenir})


def list_souvenirs(request):
    queryset = Souvenir.objects.filter(stock__gt=0, package__isnull=False).order_by('-created_at')


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
