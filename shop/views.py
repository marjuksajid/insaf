from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Cart, CartItem

def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})


def get_or_create_cart(request):
    """Helper function to get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For anonymous users, use session
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


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
    
    messages.success(request, f'{product.name} added to cart!')
    
    # Redirect back to the previous page or product detail
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            cart_item.delete()
            messages.info(request, 'Item removed from cart.')
    
    return redirect('cart')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f'{product_name} removed from cart.')
    return redirect('cart')

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'shop/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            auth_login(request, user)  # Automatically log in after registration
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'shop/register.html', {'form': form})

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