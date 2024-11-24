from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [

    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('', views.index, name='index'),
    path('add-to-bag/<int:product_id>/', views.add_to_bag, name='add_to_bag'),
    path('list/', views.product_list, name='product_list'),
    path('bag/', views.view_bag, name='view_bag'),

]
