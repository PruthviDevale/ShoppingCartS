
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    # Home
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # Products
    path('products/', views.products, name='products'),

    # Individual Product Details
    path(
        'products/<int:product_id>/',
        views.product_details,
        name='product_details'
    ),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/', views.cart, name='cart'),

    path('update-cart/<str:key>/', views.update_cart, name='update_cart'),

    path('remove-from-cart/<str:key>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),

    path('wishlist/', views.wishlist, name='wishlist'),
    
    path('add-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),

    path('remove-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

       path('', views.home, name='home'),

    path('orders/', views.orders, name='orders'),


]
