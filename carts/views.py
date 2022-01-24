#from socket import CAN_BCM_STARTTIMER
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    cart =request.session.session_key
    if not cart:
        cart = request.session.create()
        
    return cart

def add_cart(request, product_id, cartItem_id):

    product = Product.objects.get(id=product_id)
    product_variation = []

    # try para la creacion de carrito de compras si es que este no existe

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    boleano = False
    product_in_cart = False

    if request.method == "POST":
        # Detecta si el cliente selecciono una variacion
        for item in request.POST:
            key = str(item).lower()
            value = str(request.POST[key]).lower()
            try:
                variation = Variation.objects.get(product=product, category=key, value=value)
                product_variation.append(variation.id)
            except:
                pass
        if product_variation:
            product_variation = sorted(product_variation)

        # Comprueba si el producto y la variacion ya exiten en el carrito
        cart_items = CartItem.objects.all()
        cx = None
        for i in cart_items:
            if i.product == product:
                product_variation2 = []
                for iv in i.variations.all():
                    product_variation2.append(iv.id)
                if product_variation2:
                    product_variation2 = sorted(product_variation2)
                if product_variation == product_variation2:
                    product_in_cart = True
                    cx = i
        if cartItem_id == 0:
            if product_in_cart == boleano:
                # Crea el cartItem
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart
                )
                # Agrega la variacion al cartItem
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
            else:
                cx.quantity += 1
                cx.save()
        else:
            cx = CartItem.objects.get(id=cartItem_id)
            cx.quantity += 1
            cx.save()
    else:
        # Comprueba si el producto ya exiten en el carrito
        cart_items = CartItem.objects.all()
        cx = None
        for i in cart_items:
            if i.product == product and i.variations.all().count() == 0:
                product_in_cart = True
                cx = i
        if product_in_cart == boleano:
            CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
        else:
            cx.quantity += 1
            cx.save()
    return redirect('cart')
        
def remove_cart(request, product_id, cart_item_id):
    cart =Cart.objects.get(cart_id = _cart_id (request))
    product = get_object_or_404(Product, id = product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart =cart, id=cart_item_id)

        if cart_item.quantity>1:
            cart_item.quantity -= 1
            cart_item.save()

        else:
            cart_item.delete()

    except:
        pass

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id (request))
    product = get_object_or_404(Product, id = product_id)
    cart_item = CartItem.objects.get(product=product, cart =cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
    


def cart (request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    gran_total = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            
        tax = total * 0.19
        gran_total = total + tax
        
    except ObjectDoesNotExist:
        pass
    
    ctx = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'gran_total': gran_total,
    }
            
    return render(request, 'store/cart.html', ctx)
