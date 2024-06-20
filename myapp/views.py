
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .models import Cart, Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from .models import Payment
from django.core.mail import send_mail
from django.conf import settings
from .forms import MyUserCreationForm
from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer

def login_view(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('myapp:product_list')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('myapp:index.html')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'myapp/index.html', context)


def custom_logout(request):
    logout(request)
    return redirect('myapp/index.html')


def register_view(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            
            # Set backend attribute
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Adjust based on your backend configuration
            login(request, user)
            
            return redirect('myapp:index')
        else:
            messages.error(request, 'Registration was not successful')

    return render(request, 'myapp/register.html', {'form': form})

def index(request):
    return render(request, 'myapp/index.html')

@login_required
def profile_view(request):
    return render(request, 'myapp/profile.html')


@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'myapp/product_list.html', {'products': products})

def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'myapp/product_detail.html', {'product': product})


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    instance.customer.save()



def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user  # Ensure this is an instance of the correct User model

    if not isinstance(user, User):
        messages.error(request, 'Invalid user')
        return redirect('myapp:product_list')

    # Get or create a cart for the user
    cart, created = Cart.objects.get_or_create(user=user)

    # Add the product to the cart
    if product not in cart.products.all():
        cart.products.add(product)
        messages.success(request, f'{product.name} was added to your cart.')
    else:
        messages.info(request, f'{product.name} is already in your cart.')

    return redirect('myapp:cart')

def remove_from_cart_view(request):
    if request.method == "POST":
        product_ids = request.POST.getlist('product_ids')
        cart = get_object_or_404(Cart, user=request.user)
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            cart.products.remove(product)
        return redirect('myapp:cart')
    return redirect('myapp:cart')


@login_required
def cart_view(request):
    user_cart = Cart.objects.get(user=request.user)
    products_in_cart = user_cart.products.all()
    total_price = user_cart.get_total_price()

    return render(request, 'myapp/cart.html', {
        'products_in_cart': products_in_cart,
        'total_price': total_price
    })


def checkout(request):
    if request.method == 'POST':
        delivery_date = request.POST.get('delivery_date')
        delivery_time = request.POST.get('delivery_time')
        order = Order.objects.get(customer=request.user.customer, complete=False)
        order.delivery_date = delivery_date
        order.delivery_time = delivery_time
        order.complete = True
        order.save()
        return redirect('order_confirmation')
    return render(request, 'myapp/checkout.html')





@login_required
def payment_view(request):
    customer = request.user.customer
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method == 'Mpesa':
            mpesa_code = request.POST.get('mpesa_code')
            # Process Mpesa payment here
            messages.success(request, 'Payment made successfully via Mpesa.')
        elif payment_method == 'Card':
            card_number = request.POST.get('card_number')
            # Process card payment here
            messages.success(request, 'Payment made successfully via Card.')
        else:
            messages.error(request, 'Invalid payment method.')
        return redirect('myapp:payment')  # Redirect to a success or another relevant page
    return render(request, 'myapp/payment.html')




def send_order_confirmation(order):
    subject = 'Order Confirmation'
    message = f'Thank you for your order {order.customer.user.username}. Your order number is {order.id}.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [order.customer.user.email]
    send_mail(subject, message, email_from, recipient_list)

def order_confirmation(request):
    order = Order.objects.get(customer=request.user.customer, complete=True)
    send_order_confirmation(order)
    # Add SMS API call here
    return render(request, 'myapp/order_confirmation.html', {'order': order})