from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from checkout.models import Cart, CartItem
from vitrine.models import ArtWork, Souvenir
from vitrine.services.frenet import calcular_frete  # ajuste o path conforme sua estrutura

@login_required
def add_item_in_cart(request, slug, item_id):
    # Busca o produto
    product = ArtWork.objects.filter(slug=slug, id=item_id).first() or Souvenir.objects.filter(slug=slug, id=item_id).first()
    if not product:
        messages.error(request, "Produto não encontrado.")
        return redirect('/')

    # Verifica se o usuário tem endereço principal cadastrado
    # Garante que o usuário é cliente e tem endereço principal
    if not hasattr(request.user, 'client'):
        messages.warning(request, "Você precisa ter um perfil de cliente para adicionar produtos ao carrinho.")
        return redirect('/')

    endereco_cliente = request.user.client.addresses.filter(principal=True).first()
    if not endereco_cliente:
        messages.warning(request, "Você precisa cadastrar um endereço principal antes de adicionar produtos ao carrinho.")
        return redirect('/')


    if not endereco_cliente:
        messages.warning(request, "Você precisa cadastrar um endereço antes de adicionar produtos ao carrinho.")
        return redirect('/')  # ajuste para sua rota de perfil/endereço

    # Verifica se o artista tem endereço
    endereco_artista = getattr(product.artist, 'addresses', None)
    if not endereco_artista:
        messages.error(request, "O artista não possui endereço cadastrado, impossível calcular o frete.")
        return redirect(product.get_absolute_url())
    endereco_artista = endereco_artista.filter(principal=True).first()

    if not endereco_artista:
        messages.error(request, "O artista não possui um endereço principal cadastrado.")
        return redirect(product.get_absolute_url())

    # Quantidade
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect(product.get_absolute_url())

    # Estoque
    available_stock = getattr(product, 'stock', 1)
    if quantity > available_stock:
        messages.error(request, f"Quantidade solicitada excede o estoque disponível ({available_stock}).")
        return redirect(product.get_absolute_url())

    # Pega a embalagem associada ao produto
    package = getattr(product, 'package', None)
    if not package:
        messages.error(request, "Nenhuma embalagem cadastrada para este produto.")
        return redirect(product.get_absolute_url())

    # Calcula o frete automaticamente
    peso_total = package.weight * quantity
    valor_total = float(product.price) * quantity
    resultado_frete = calcular_frete(
        origem_cep=endereco_artista.cep,
        destino_cep=endereco_cliente.cep,
        peso=peso_total,
        altura=package.height,
        largura=package.width,
        comprimento=package.length,
        valor=valor_total
    )

    # Filtra os serviços válidos
    fretes_validos = [
        s for s in resultado_frete.get("ShippingSevicesArray", [])
        if not s.get("Error", True)
    ]

    if not fretes_validos:
        messages.error(request, "Não foi possível calcular o frete para este produto.")
        return redirect(product.get_absolute_url())

    # Escolhe o mais barato automaticamente (ou você pode exibir no frontend)
    melhor_frete = min(fretes_validos, key=lambda x: float(x["ShippingPrice"]))

    # Obtém o carrinho do usuário
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Cria ou atualiza o item
    if isinstance(product, ArtWork):
        cart_item, created = CartItem.objects.get_or_create(cart=cart, artwork=product)
    else:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, souvenir=product)

    # Atualiza informações
    cart_item.quantity = quantity
    cart_item.shipping_type = melhor_frete["ServiceDescription"]
    cart_item.shipping_value = melhor_frete["ShippingPrice"]
    cart_item.full_clean()
    cart_item.save()

    cart.save()
    messages.success(request, f"Item adicionado ao carrinho com frete {melhor_frete['ServiceDescription']} - R${melhor_frete['ShippingPrice']}")
    return redirect('checkout:cart_detail')


# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib.auth.decorators import login_required
# from checkout.models import Cart, CartItem
# from vitrine.models import ArtWork, Souvenir
# from django.contrib import messages

# @login_required
# def add_item_in_cart(request, slug, item_id):
#     product = ArtWork.objects.filter(slug=slug, id=item_id).first() or Souvenir.objects.filter(slug=slug, id=item_id).first()
#     if not product:
#         messages.error(request, "Produto não encontrado.")
#         return redirect('/')

#     cart, _ = Cart.objects.get_or_create(user=request.user)

#     # Quantidade vinda do formulário
#     try:
#         quantity = int(request.POST.get('quantity', 1))
#     except ValueError:
#         messages.error(request, "Quantidade inválida.")
#         return redirect(product.get_absolute_url())

#     # Verifica estoque disponível
#     available_stock = product.stock
#     if quantity > available_stock:
#         messages.error(request, f"Quantidade solicitada excede o estoque disponível ({available_stock}).")
#         return redirect(product.get_absolute_url())

#     # Cria ou atualiza o item no carrinho
#     if isinstance(product, ArtWork):
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, artwork=product)
#     else:
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, souvenir=product)

#     if created:
#         cart_item.quantity = quantity
#     else:
#         new_quantity = cart_item.quantity + quantity
#         if new_quantity > available_stock:
#             messages.error(request, f"Você já tem {cart_item.quantity} no carrinho. Adicionar mais excederia o estoque.")
#             return redirect(product.get_absolute_url())
#         cart_item.quantity = new_quantity

#     cart_item.full_clean()
#     cart_item.save()
#     cart.save()

#     messages.success(request, "Item adicionado ao carrinho.")
#     return redirect('checkout:cart_detail')


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
            item.save()
            messages.success(request, "Quantidade atualizada.")
    except ValueError:
        messages.error(request, "Quantidade inválida.")

    cart.save()
    return redirect('checkout:cart_detail')


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).all().order_by('-id')
    context = {
        'cart': cart,
        'cart_items': cart_items
    }
    return render(request, 'checkout/cart_detail.html', context)
