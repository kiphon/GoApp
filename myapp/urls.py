from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView
from .views import remove_from_cart_view, add_to_cart_view

app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    #path('accounts/login/', views.LoginView.as_view(), name='login'),
    #path('accounts/profile/', views.profile_view, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    #path('product/<int:product_id>/', views.product_detail, name='ProductDetail'),
   path('add-to-cart/<int:product_id>/', add_to_cart_view, name='add_to_cart'),
    path('remove-from-cart/', remove_from_cart_view, name='remove_from_cart'),  # Update this line
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment_view, name='payment'),
    path('send-order-confirmation/', views.send_order_confirmation, name='SendOrderConfirmation'),
    path('order-confirmation/', views.order_confirmation, name='OrderConfirmation'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)