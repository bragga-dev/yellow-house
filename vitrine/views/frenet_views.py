from django.shortcuts import render
from vitrine.services.frenet import calcular_frete
from django.http import JsonResponse

def calcular_frete_view(request):
    resultado = None

    if request.method == "POST":
        cep_origem = "01001000"  
        cep_destino = request.POST.get("cep_destino")
        peso = request.POST.get("peso")
        comprimento = request.POST.get("comprimento")
        largura = request.POST.get("largura")
        altura = request.POST.get("altura")

        resultado = calcular_frete(cep_origem, cep_destino, peso, largura, altura, comprimento)

    return render(request, "frete/calcular_frete.html", {"resultado": resultado})



def calcular_frete_view(request):
    resultado = calcular_frete(
        origem_cep='04547000',
        destino_cep='40100100',
        peso=1.2,
        altura=10,
        largura=15,
        comprimento=20,
        valor=150.00
    )
    return JsonResponse(resultado)
