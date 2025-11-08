from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from checkout.models import Cart, CartItem
from vitrine.models import ArtWork, Souvenir
from vitrine.utils import calcular_frete_item
from django.http import JsonResponse
import json
from decimal import Decimal, InvalidOperation
from user.models import Client
@login_required
def add_item_in_cart(request, slug, item_id):
    product = ArtWork.objects.filter(slug=slug, id=item_id).first() or Souvenir.objects.filter(slug=slug, id=item_id).first()
    if not product:
        messages.error(request, "Produto não encontrado.")
        return redirect('/')

    if not hasattr(request.user, 'client') and not hasattr(request.user, 'artist'):
        messages.warning(request, "Você precisa ter um perfil de cliente para adicionar produtos ao carrinho.")
        return redirect('/')
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect(product.get_absolute_url())

    available_stock = getattr(product, 'stock', 1)
    if quantity > available_stock:
        messages.error(request, f"Quantidade solicitada excede o estoque disponível ({available_stock}).")
        return redirect(product.get_absolute_url())

    cart, _ = Cart.objects.get_or_create(user=request.user)

    if isinstance(product, ArtWork):
        cart_item, created = CartItem.objects.get_or_create(cart=cart, artwork=product)
    else:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, souvenir=product)

    cart_item.quantity = quantity
    cart_item.unit_price = product.price
    cart_item.shipping_type = None
    cart_item.shipping_value = Decimal('0.00')
    cart_item.full_clean()
    cart_item.save()

    cart.save()
    messages.success(request, "Item adicionado ao carrinho. Escolha o frete desejado abaixo do item.")
    return redirect('checkout:cart_detail')



@login_required
def remove_item_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    cart.save()
    messages.success(request, "Item removido do carrinho.")
    return redirect('checkout:cart_detail')


@login_required
def update_item_quantity(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity < 1:
            item.delete()
            messages.info(request, "Item removido por quantidade zero.")
        else:
            item.quantity = new_quantity
            item.shipping_type = None  # Resetar frete para forçar nova seleção
            item.shipping_value = Decimal('0.00')
            item.save()
            messages.success(request, "Quantidade atualizada. Selecione o frete novamente.")
    except ValueError:
        messages.error(request, "Quantidade inválida.")

    cart.update_totals()  # Garantir que os totais são atualizados
    return redirect('checkout:cart_detail')

import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from checkout.models import Cart, CartItem
from vitrine.utils import calcular_frete_item

logger = logging.getLogger(__name__)

@login_required
def cart_detail(request):
    """Exibe o carrinho de compras do usuário com cálculo de frete por item."""

    # Obtém ou cria o carrinho do usuário
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).order_by('-id')

    endereco_cliente = None
    cep_destino = None

    # Identifica se o usuário é cliente ou artista
    try:
        if hasattr(request.user, 'client'):
            endereco_cliente = request.user.client.addresses.filter(principal=True).first()
        elif hasattr(request.user, 'artist'):
            endereco_cliente = request.user.artist.addresses.filter(principal=True).first()
    except Exception as e:
        logger.error(f"Erro ao buscar endereço do usuário {request.user.id}: {e}")

    if endereco_cliente and endereco_cliente.cep:
        cep_destino = endereco_cliente.cep
    else:
        messages.warning(request, "Não foi possível determinar o endereço de entrega. Verifique seus dados.")
        logger.warning(f"Usuário {request.user.id} sem endereço principal definido.")

    fretes_itens = {}

    for item in cart_items:
        produto = item.artwork or item.souvenir
        endereco_origem = getattr(produto, 'artist', None)
        cep_origem = None

        if endereco_origem and hasattr(endereco_origem, 'addresses'):
            endereco_origem = endereco_origem.addresses.filter(principal=True).first()
            cep_origem = endereco_origem.cep if endereco_origem else None

        package = getattr(produto, 'package', None)

        if not all([cep_origem, cep_destino, package]):
            fretes_itens[item.id] = {"error": "Dados insuficientes para calcular o frete."}
            continue

        try:
            resultado = calcular_frete_item(
                origem_cep=cep_origem,
                destino_cep=cep_destino,
                package=package,
                valor_unitario=produto.price,
                quantidade=item.quantity
            )
            fretes_itens[item.id] = resultado
        except Exception as e:
            logger.error(f"Erro ao calcular frete para o item {item.id}: {e}")
            fretes_itens[item.id] = {"error": "Erro ao calcular o frete deste item."}

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'fretes_itens': fretes_itens,
    }
    return render(request, 'checkout/cart_detail.html', context)





@login_required
def update_shipping(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        service_code = data.get('service_code')
        shipping_price = data.get('shipping_price', '0')

        try:
            # Garantir que o preço do frete seja Decimal com precisão correta
            shipping_price = Decimal(str(shipping_price)).quantize(Decimal('0.01'))
        except (InvalidOperation, TypeError, ValueError):
            shipping_price = Decimal('0.00')

        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        item.shipping_type = service_code
        item.shipping_value = shipping_price
        item.save()

        cart.update_totals()

        return JsonResponse({
            'success': True,
            'shipping_type': service_code,
            'shipping_value': f"{shipping_price:.2f}",
            'total_shipping': f"{cart.total_shipping:.2f}",
            'total_price': f"{cart.total_price:.2f}",
            'total_geral': f"{cart.total_geral:.2f}",
            'item_subtotal': f"{item.subtotal():.2f}"
        })

    return JsonResponse({'success': False}, status=400)