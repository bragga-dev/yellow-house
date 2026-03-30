# checkout/views/payment_views.py
import mercadopago
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from checkout.models import Cart, Order, Payment
from checkout.services import OrderService, PaymentService
import logging

logger = logging.getLogger(__name__)




@login_required
@csrf_exempt
def create_pix_payment(request):
    """Cria pagamento via PIX"""
    try:
        cart = Cart.objects.get(user=request.user)

        if not cart.items.exists():
            logger.warning("Carrinho vazio")
            return JsonResponse({"success": False, "error": "Carrinho vazio"}, status=400)

        logger.info(f"Carrinho encontrado com {cart.items.count()} itens para usuário {request.user.email}")

        # 1. Criar pedido
        try:
            order = OrderService.create_order_from_cart(cart, "pix")
            logger.info(f"Pedido criado: {order.order_code} total={order.order_total_geral}")
        except Exception as e:
            logger.error(f"Erro ao criar ordem: {e}", exc_info=True)
            return JsonResponse({"success": False, "error": f"Erro ao criar pedido: {str(e)}"}, status=500)

        # 2. Criar pagamento PIX no Mercado Pago
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

        # LOG do token mascarado
        masked_token = settings.MP_ACCESS_TOKEN[:10] + "..." + settings.MP_ACCESS_TOKEN[-5:]
        logger.info(f"Usando Access Token: {masked_token}")

        # CPF normalizado
        raw_cpf = request.user.cpf
        cpf_user = (raw_cpf or "").replace(".", "").replace("-", "")
        logger.info(f"CPF do usuário (raw): {raw_cpf}")
        logger.info(f"CPF enviado ao MP: {cpf_user}")

        # Garantir que email e nome existem
        logger.info(f"Email usuário: {request.user.email}")
        logger.info(f"Nome usuário: {request.user.first_name} {request.user.last_name}")

        # Garantir que CPF exista
        logger.info(f"CPF usuário: {request.user.cpf}")
        cpf_user = (request.user.cpf or "").replace(".", "").replace("-", "")
        logger.info(f"CPF enviado ao MP: {cpf_user}")

        payment_data = {
         "transaction_amount": float(order.order_total_geral),
            "description": f"Pedido {order.order_code}",
            "payment_method_id": "pix",
            "payer": {
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "identification": {
                    "type": "CPF",
                    "number": cpf_user
                }
            },
            "external_reference": str(order.id)
        }

        # Só adiciona notification_url se existir
        if settings.MP_WEBHOOK_URL:
            payment_data["notification_url"] = settings.MP_WEBHOOK_URL

        logger.info("Pagamento enviado ao Mercado Pago (REFATORADO):")
        logger.info(json.dumps(payment_data, indent=2))

        payment_response = sdk.payment().create(payment_data)


        logger.info(f"Pagamento enviado ao Mercado Pago: {json.dumps(payment_data, indent=2)}")

        payment_response = sdk.payment().create(payment_data)

        logger.info(f"Resposta completa do Mercado Pago: {json.dumps(payment_response, indent=2)}")

        # Se status != 201 — erro
        if payment_response["status"] != 201:
            logger.error("⚠ ERRO NO MERCADO PAGO ⚠")
            logger.error(json.dumps(payment_response, indent=2))

            # Se houver "causes"
            causes = payment_response.get("response", {}).get("cause")
            if causes:
                logger.error(f"Causes do erro: {causes}")

            return JsonResponse({
                "success": False,
                "error": "Erro ao criar pagamento PIX no Mercado Pago"
            }, status=400)

        payment_info = payment_response["response"]

        # 3. Salvar informações do pagamento
        try:
            PaymentService.create_payment_record(order, payment_info)
            logger.info(f"Pagamento registrado no banco com ID MP: {payment_info.get('id')}")
        except Exception as e:
            logger.error(f"Erro ao salvar pagamento: {e}", exc_info=True)

        # 4. Retornar dados do PIX
        pix_data = payment_info.get("point_of_interaction", {}).get("transaction_data", {})
        logger.info("PIX gerado com sucesso")

        return JsonResponse({
            "success": True,
            "payment_id": payment_info["id"],
            "qr_code_base64": pix_data.get("qr_code_base64"),
            "qr_code": pix_data.get("qr_code"),
            "order_id": str(order.id),
            "order_code": order.order_code,
        })

    except Cart.DoesNotExist:
        logger.error("Carrinho não encontrado para o usuário")
        return JsonResponse({"success": False, "error": "Carrinho não encontrado"}, status=404)

    except Exception as e:
        logger.error(f"Erro geral em create_pix_payment: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": "Erro interno do servidor"}, status=500)


@login_required
def pix_payment_view(request, order_id):
    """Página de pagamento PIX"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = order.payments.first()

    if not payment:
        return render(request, "checkout/error.html", {"error": "Pagamento não encontrado"})

    pix_data = payment.raw_data.get("point_of_interaction", {}).get("transaction_data", {})

    context = {
        "order": order,
        "payment": payment,
        "qr_code_base64": pix_data.get("qr_code_base64"),
        "qr_code": pix_data.get("qr_code"),
    }
    return render(request, "checkout/pix_payment.html", context)


@login_required
def payment_success(request):
    """Página de sucesso de pagamento"""
    return render(request, "checkout/payment_success.html")
