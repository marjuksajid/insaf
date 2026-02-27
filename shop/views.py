from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Product, Cart, CartItem, OrderItem
from .forms import OrderForm

def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart = Cart.objects.filter(session_key=session_key, order__isnull=True).first()
    if cart:
        return cart
    return Cart.objects.create(session_key=session_key)


def cart(request):
    cart_obj = get_or_create_cart(request)
    cart_items = cart_obj.items.all()
    total = cart_obj.get_total()
    item_count = cart_obj.get_item_count()
    
    context = {
        'cart': cart_obj,
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_obj = get_or_create_cart(request)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # If item already exists, increase quantity
        cart_item.quantity += 1
        cart_item.save()
        
    # Redirect back to the previous page or product detail
    referer = request.META.get("HTTP_REFERER")
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}
    ):
        return redirect(referer)
    return redirect(reverse("home"))


@require_POST
def update_cart(request, item_id):
    cart_obj = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart_obj)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("cart")

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


@require_POST
def remove_from_cart(request, item_id):
    cart_obj = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart_obj)
    cart_item.delete()
    return redirect('cart')


def checkout(request):
    cart_obj = get_or_create_cart(request)
    cart_items = cart_obj.items.all()
    
    if request.method == 'POST':
        if cart_obj.get_item_count() == 0:
            messages.error(request, "Your cart is empty. Please add items to checkout.")
            return redirect('cart')

        form = OrderForm(request.POST)
        if not form.is_valid():
            messages.error(request, "All fields are required.")
            return render(request, "shop/checkout.html", {"form": form, "cart_items": cart_items})

        cart_items = list(cart_obj.items.select_related('product'))
        total = sum(item.get_subtotal() for item in cart_items)

        with transaction.atomic():
            order = form.save(commit=False)
            order.cart = cart_obj
            order.total_amount = total
            order.save()

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=item.product.price,
                    subtotal=item.get_subtotal(),
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            # Clear the cart after order is placed
            cart_obj.items.all().delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('home')

    return render(request, 'shop/checkout.html', {"form": OrderForm(), "cart_items": cart_items})

def product_detail(request, link):
    product = get_object_or_404(Product, link=link)
    return render(request, 'shop/product_page.html', {'product': product})
# The link is generated automatically based on the product's name or ID when the product is saved.
# In the `save` method of the `Product` model, 
# the `link` field is set to a slugified version of the product's name 
# if it is not already set. This means that when you create a new product and save it, 
# the `link` field will be automatically populated 
# with a URL-friendly version of the product's name, which can then be used in the URL for the product detail page. 
# You do not need to manually create or set the link; it will be generated for you when you save the product.

def terms(request):
    return render(request, 'shop/terms.html')
