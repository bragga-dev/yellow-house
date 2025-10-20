from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from checkout.models import Cart, CartItem
from vitrine.models import ArtWork, Souvenir
from django.contrib import messages

@login_required
def add_item_in_cart(request, slug, item_id):
    product = ArtWork.objects.filter(slug=slug, id=item_id).first() or Souvenir.objects.filter(slug=slug, id=item_id).first()
    if not product:
        messages.error(request, "Produto não encontrado.")
        return redirect('vitrine:home')

    cart, _ = Cart.objects.get_or_create(user=request.user)

    if isinstance(product, ArtWork):
        cart_item, created = CartItem.objects.get_or_create(cart=cart, artwork=product)
    else:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, souvenir=product)

    if not created:
        cart_item.quantity += 1
    cart_item.full_clean()
    cart_item.save()

    cart.save()  
    messages.success(request, "Item adicionado ao carrinho.")
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
