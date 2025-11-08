
from .models import Cart

def cart_context(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return {
            'cart': cart,
            'cart_items': cart.items.all(),
            'cart_total': cart.total_price,
        }
    return {
        'cart': None,
        'cart_items': [],
        'cart_total': 0,
    }
