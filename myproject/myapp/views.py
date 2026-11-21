
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import Order, Product


# HOME PAGE
def home(request):

    product_list = Product.objects.all()[:8]

    return render(
        request,
        'accounts/home.html',
        {'products': product_list}
    )


# REGISTER
def register(request):

    if request.method == 'POST':

        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html')

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        messages.success(
            request,
            'Registration successful! Please login.'
        )

        return redirect('login')

    return render(request, 'accounts/register.html')


# DISPLAY PRODUCTS WITH CATEGORY AND SEARCH
def products(request):

    product_list = Product.objects.all()

    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '').strip()

    if category:
        product_list = product_list.filter(category=category)

    if search_query:
        product_list = product_list.filter(
            name__icontains=search_query
        )

    return render(
        request,
        'accounts/products.html',
        {
            'products': product_list,
            'selected_category': category,
            'search_query': search_query
        }
    )


# LOGIN
def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


# LOGOUT
def user_logout(request):

    auth_logout(request)

    return redirect('home')


# PRODUCT DETAILS
def product_details(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    return render(
        request,
        'accounts/product_details.html',
        {'product': product}
    )


# ADD TO CART
@login_required
@require_POST
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    size = request.POST.get('size')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 0

    if size not in ['S', 'M', 'L', 'XL'] or quantity < 1 or quantity > 10:

        messages.error(
            request,
            'Please select a valid size and quantity.'
        )

        return redirect('product_details', product_id=product_id)

    cart_data = request.session.get('cart', {})

    key = f"{product_id}_{size}"

    if key in cart_data:

        cart_data[key]['quantity'] += quantity

    else:

        cart_data[key] = {
            'product_id': product_id,
            'size': size,
            'quantity': quantity
        }

    request.session['cart'] = cart_data

    messages.success(
        request,
        'Product added to your cart!'
    )

    return redirect('cart')


# VIEW CART
@login_required
def cart(request):

    cart_data = request.session.get('cart', {})

    cart_items = []
    total_price = Decimal('0.00')
    total_items = 0

    for key, value in cart_data.items():

        product = Product.objects.filter(
            id=value['product_id']
        ).first()

        if product:

            quantity = value['quantity']
            subtotal = product.price * quantity

            cart_items.append({
                'key': key,
                'product': product,
                'size': value['size'],
                'quantity': quantity,
                'subtotal': subtotal
            })

            total_price += subtotal
            total_items += quantity

    return render(
        request,
        'accounts/cart.html',
        {
            'cart_items': cart_items,
            'total_price': total_price,
            'total_items': total_items
        }
    )


# UPDATE CART
@login_required
@require_POST
def update_cart(request, key):

    cart_data = request.session.get('cart', {})

    if key in cart_data:

        try:

            quantity = int(request.POST.get('quantity', 1))

            if 1 <= quantity <= 10:

                cart_data[key]['quantity'] = quantity
                request.session['cart'] = cart_data

                messages.success(
                    request,
                    'Cart updated successfully.'
                )

            else:

                messages.error(
                    request,
                    'Quantity must be between 1 and 10.'
                )

        except (ValueError, TypeError):

            messages.error(
                request,
                'Invalid quantity.'
            )

    return redirect('cart')


# REMOVE FROM CART
@login_required
@require_POST
def remove_from_cart(request, key):

    cart_data = request.session.get('cart', {})

    if key in cart_data:

        del cart_data[key]

        request.session['cart'] = cart_data

        messages.success(
            request,
            'Product removed from cart.'
        )

    return redirect('cart')


# CHECKOUT
@login_required
def checkout(request):

    cart_data = request.session.get('cart', {})

    cart_items = []
    total_price = Decimal('0.00')
    total_items = 0

    for key, value in cart_data.items():

        product = Product.objects.filter(
            id=value['product_id']
        ).first()

        if product:

            quantity = int(value['quantity'])
            subtotal = product.price * quantity

            cart_items.append({
                'key': key,
                'product': product,
                'size': value['size'],
                'quantity': quantity,
                'subtotal': subtotal
            })

            total_price += subtotal
            total_items += quantity

    if not cart_items:

        messages.error(
            request,
            'Your shopping cart is empty.'
        )

        return redirect('products')

    if request.method == 'POST':

        request.session['shipping_details'] = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'city': request.POST.get('city'),
            'pincode': request.POST.get('pincode'),
            'payment_method': request.POST.get('payment_method')
        }

        messages.success(
            request,
            'Delivery details saved successfully!'
        )

    return render(
        request,
        'accounts/checkout.html',
        {
            'cart_items': cart_items,
            'total_price': total_price,
            'total_items': total_items
        }
    )


# VIEW WISHLIST
@login_required
def wishlist(request):

    wishlist_ids = request.session.get('wishlist', [])

    wishlist_items = Product.objects.filter(
        id__in=wishlist_ids
    )

    return render(
        request,
        'accounts/wishlist.html',
        {
            'wishlist_items': wishlist_items
        }
    )


# ADD TO WISHLIST
@login_required
@require_POST
def add_to_wishlist(request, product_id):

    get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_ids = request.session.get('wishlist', [])

    product_id = int(product_id)

    if product_id not in wishlist_ids:

        wishlist_ids.append(product_id)

    request.session['wishlist'] = wishlist_ids

    messages.success(
        request,
        'Product added to your wishlist!'
    )

    return redirect('wishlist')


# REMOVE FROM WISHLIST
@login_required
@require_POST
def remove_from_wishlist(request, product_id):

    wishlist_ids = request.session.get('wishlist', [])

    product_id = int(product_id)

    if product_id in wishlist_ids:

        wishlist_ids.remove(product_id)

    request.session['wishlist'] = wishlist_ids

    messages.success(
        request,
        'Product removed from your wishlist.'
    )

    return redirect('wishlist')


# MY ORDERS
@login_required(login_url='login')
def orders(request):

    order_list = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'accounts/orders.html',
        {
            'orders': order_list
        }
    )
