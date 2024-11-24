from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from products.models import Product, Category, SubCategory, Review
from users.models import Wishlist
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Index view to list products on the main page
def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


# Product List View
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get('q')
    category_filter = request.GET.get('category')
    subcategory_filter = request.GET.get('subcategory')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_filter:
        products = products.filter(category__id=category_filter)
    if subcategory_filter:
        products = products.filter(subcategory__id=subcategory_filter)

    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'subcategories': subcategories,
    })


# Product Detail View
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
    })


# Add to Wishlist View
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        wishlist_item.save()
    return redirect('product_detail', product_id=product_id)


def add_to_bag(request, product_id):
    # Get the product using product_id
    product = get_object_or_404(Product, id=product_id)

    # Retrieve the bag from session or create an empty bag
    bag = request.session.get('bag', {})

    # If the product is already in the bag, increment the quantity
    if str(product_id) in bag:
        bag[str(product_id)] += 1
    else:
        # If not in the bag, add it with a quantity of 1
        bag[str(product_id)] = 1

    # Update the session bag
    request.session['bag'] = bag

    # Success message for adding to bag
    messages.success(request, f"{product.name} has been added to your bag.")
    return redirect('products:product_list')


def index(request):
    products = Product.objects.all()
    return render(request, 'products/index.html', {'products': products})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def view_bag(request):
    # Retrieve the bag from session
    bag = request.session.get('bag', {})

    # Get product information from bag
    product_ids = bag.keys()
    products = Product.objects.filter(id__in=product_ids)

    # Add quantity to product details
    products_with_quantity = []
    for product in products:
        products_with_quantity.append({
            'product': product,
            'quantity': bag[str(product.id)],
        })

    return render(request, 'products/bag.html', {'products': products_with_quantity})
