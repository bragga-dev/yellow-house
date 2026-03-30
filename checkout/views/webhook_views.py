# checkout/views/webhook_views.py
import json
import logging
import mercadopago
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from checkout.models import Order, Payment
from checkout.services import PaymentService

logger = logging.getLogger(__name__)

@csrf_exempt
def mercadopago_webhook(request):
    """Webhook para notificações do Mercado Pago"""
    if request.method != 'POST':
        return JsonResponse({"status": "method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        logger.info(f"Webhook recebido: {payload}")

        if 'data' not in payload or 'id' not in payload['data']:
            return JsonResponse({"status": "invalid payload"}, status=400)

        payment_id = payload['data']['id']

        # Buscar informações do pagamento no Mercado Pago
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment_id)
        
        if payment_info['status'] != 200:
            return JsonResponse({"status": "payment not found"}, status=404)

        payment_data = payment_info['response']
        status = payment_data.get('status')
        order_id = payment_data.get('external_reference')

        if not order_id:
            return JsonResponse({"status": "missing order reference"}, status=400)

        # Buscar e atualizar pedido
        try:
            order = Order.objects.get(id=order_id)
            
            # Atualizar ou criar pagamento
            payment, created = Payment.objects.update_or_create(
                mp_id=payment_id,
                defaults={
                    'order': order,
                    'status': status.upper(),
                    'amount': payment_data.get('transaction_amount'),
                    'raw_data': payment_data
                }
            )

            # Atualizar status do pedido
            PaymentService.update_order_status(order, status)

            logger.info(f"Pedido {order.order_code} atualizado para status: {status}")
            return JsonResponse({"status": "processed"})

        except Order.DoesNotExist:
            logger.error(f"Pedido não encontrado: {order_id}")
            return JsonResponse({"status": "order not found"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"status": "invalid json"}, status=400)
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return JsonResponse({"status": "error"}, status=500)