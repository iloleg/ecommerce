from django.urls import path
from . import views

urlpatterns = [
    path('sales-report/', views.sales_report, name='sales_report'),
    path('user-activity-report/', views.user_activity_report, name='user_activity_report'),
    path('most-purchased-products/', views.most_purchased_products, name='most_purchased_products'),
    path('sales-statistics-by-product/', views.sales_statistics_by_product, name='sales_statistics_by_product'),
]
