# checkout/services.py - VERSÃO CORRIGIDA
import logging
from django.contrib.contenttypes.models import ContentType
from checkout.models import Order, OrderItem, Cart, Payment
from vitrine.models import ArtWork, Souvenir
from decimal import Decimal

logger = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    def create_order_from_cart(cart: Cart, payment_method: str) -> Order:
        """
        Cria um pedido a partir do carrinho - CORRIGIDO para CartItem sem content_object
        """
        try:
            # Criar o pedido com os campos corretos
            order = Order.objects.create(
                order_user=cart.user,
                order_payment_method=payment_method,
                order_subtotal=cart.total_price,
                order_shipping_total=cart.total_shipping,
                order_total_geral=cart.total_geral
            )

            # Criar itens do pedido - CORREÇÃO: tratar artwork e souvenir separadamente
            for cart_item in cart.items.all():
                if cart_item.artwork:
                    # É uma obra de arte
                    content_type = ContentType.objects.get_for_model(ArtWork)
                    object_id = cart_item.artwork.id
                    product_name = cart_item.artwork.name
                elif cart_item.souvenir:
                    # É um souvenir
                    content_type = ContentType.objects.get_for_model(Souvenir)
                    object_id = cart_item.souvenir.id
                    product_name = cart_item.souvenir.name
                else:
                    # Item sem produto associado - pular
                    logger.warning(f"CartItem {cart_item.id} sem produto associado")
                    continue

                OrderItem.objects.create(
                    order=order,
                    order_item_quantity=cart_item.quantity,
                    order_item_price=cart_item.unit_price,
                    content_type=content_type,
                    object_id=object_id
                )

                logger.info(f"Item do pedido criado: {product_name}")

            # Limpar carrinho após criar pedido
            cart.items.all().delete()
            cart.total_price = 0
            cart.total_shipping = 0
            cart.total_geral = 0
            cart.save()

            logger.info(f"Pedido {order.order_code} criado com sucesso com {order.order_item.count()} itens")
            return order

        except Exception as e:
            logger.error(f"Erro ao criar pedido do carrinho: {e}")
            raise

class PaymentService:
    @staticmethod
    def create_payment_record(order: Order, mp_payment_data: dict) -> Payment:
        """
        Cria registro de pagamento no banco
        """
        try:
            # Mapear status do Mercado Pago para seu modelo
            status_map = {
                'pending': 'pendente',
                'approved': 'aprovado', 
                'cancelled': 'cancelado',
                'rejected': 'rejeitado',
                'refunded': 'rejeitado'
            }
            
            mp_status = mp_payment_data.get("status", "pending")
            payment_status = status_map.get(mp_status, 'pendente')

            payment = Payment.objects.create(
                payment_order=order,
                mp_payment_id=mp_payment_data.get("id"),
                payment_status=payment_status,
                payment_amount=Decimal(str(mp_payment_data.get("transaction_amount", 0))),
                payment_method="pix",
                # Campos opcionais
                date_approved=mp_payment_data.get("date_approved"),
                date_of_expiration=mp_payment_data.get("date_of_expiration"),
                date_last_updated=mp_payment_data.get("date_last_updated"),
            )
            return payment
        except Exception as e:
            logger.error(f"Erro ao criar registro de pagamento: {e}")
            raise

    @staticmethod
    def update_order_status(order: Order, status: str):
        """
        Atualiza status do pedido baseado no pagamento
        """
        status_map = {
            'approved': Order.Status.COMPLETED,  # Usar COMPLETED em vez de PAID
            'cancelled': Order.Status.CANCELLED,
            'rejected': Order.Status.CANCELLED,
            'refunded': Order.Status.REFUNDED,
            'pending': Order.Status.PENDING,
        }
        
        new_status = status_map.get(status, Order.Status.PENDING)
        order.order_status = new_status
        order.save()
        logger.info(f"Status do pedido {order.order_code} atualizado para: {new_status}")