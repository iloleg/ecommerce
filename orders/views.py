from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CartItem, Order, OrderItem
from products.models import Product
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# View Cart
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


# Add Product to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')


# Remove Product from Cart
@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('view_cart')


# Update Cart Item Quantity
@login_required
def update_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('view_cart')


# Checkout View
@login_required
def checkout(request):
    if request.method == 'POST':
        delivery_address = request.POST['delivery_address']
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.get_total_price() for item in cart_items)

        # Create Order
        order = Order.objects.create(user=request.user, delivery_address=delivery_address, total_price=total_price,
                                     status='Pending')
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.selling_price,
                total_price=item.get_total_price()
            )
        cart_items.delete()

        # Payment Integration (Stripe)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Order {order.id}',
                        },
                        'unit_amount': int(total_price * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/order-confirmation/'),
            cancel_url=request.build_absolute_uri('/view-cart/'),
        )
        return redirect(session.url, code=303)
    else:
        return render(request, 'orders/checkout.html')


# Order Confirmation View
@login_required
def order_confirmation(request):
    return render(request, 'orders/order_confirmation.html')
