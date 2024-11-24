from django.shortcuts import render
from django.db.models import Sum, Count
from orders.models import Order, OrderItem
from products.models import Product
from .models import SalesReport, UserActivity, MostPurchasedProduct
from datetime import timedelta, date
from django.utils import timezone


# Sales Report View
def sales_report(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    daily_sales = Order.objects.filter(created_at__date=today).aggregate(total=Sum('total_price'))
    weekly_sales = Order.objects.filter(created_at__date__gte=start_of_week).aggregate(total=Sum('total_price'))
    monthly_sales = Order.objects.filter(created_at__date__gte=start_of_month).aggregate(total=Sum('total_price'))

    return render(request, 'reports/sales_report.html', {
        'daily_sales': daily_sales['total'] or 0,
        'weekly_sales': weekly_sales['total'] or 0,
        'monthly_sales': monthly_sales['total'] or 0,
    })


# User Activity Report View
def user_activity_report(request):
    activities = UserActivity.objects.all().order_by('-timestamp')
    return render(request, 'reports/user_activity_report.html', {'activities': activities})


# Most Purchased Products Report View
def most_purchased_products(request):
    products = Product.objects.annotate(purchase_count=Sum('orderitem__quantity')).order_by('-purchase_count')[:10]
    return render(request, 'reports/most_purchased_products.html', {'products': products})


# Sales Statistics by Product View
def sales_statistics_by_product(request):
    products = Product.objects.annotate(total_sales=Sum('orderitem__total_price')).order_by('-total_sales')
    return render(request, 'reports/sales_statistics_by_product.html', {'products': products})
