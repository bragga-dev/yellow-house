# checkout/views/checkout_views.py
import mercadopago
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from checkout.models import Cart, Order
from checkout.services import OrderService

@login_required
def checkout_view(request):
    """Página inicial do checkout"""
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, "checkout/checkout.html", {"cart": cart})

@login_required
def create_checkout(request):
    """Cria pedido e preferência de pagamento no Mercado Pago - COM CAMPOS CORRETOS"""
    try:
        cart = Cart.objects.get(user=request.user)
        
        if not cart.items.exists():
            return JsonResponse({"error": "Carrinho vazio"}, status=400)

        # 1. Criar pedido
        order = OrderService.create_order_from_cart(cart, "mercadopago")

        # 2. Criar preferência no Mercado Pago
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        
        preference_data = {
            "items": [
                {
                    "title": f"Pedido {order.order_code}",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(order.order_total_geral)  # CORRETO - com prefixo
                }
            ],
            "external_reference": str(order.id),
            "notification_url": settings.MP_WEBHOOK_URL,
            "back_urls": {
                "success": settings.MP_SUCCESS_URL,
                "failure": settings.MP_FAILURE_URL,
                "pending": settings.MP_PENDING_URL
            },
            "auto_return": "approved",
        }

        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] != 201:
            return JsonResponse({"error": "Erro ao criar preferência de pagamento"}, status=400)

        init_point = preference_response["response"]["init_point"]

        return JsonResponse({
            "payment_url": init_point,
            "order_id": str(order.id),
            "order_code": order.order_code,
        })

    except Cart.DoesNotExist:
        return JsonResponse({"error": "Carrinho não encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)