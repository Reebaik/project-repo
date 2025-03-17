from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from .models import Jewelry, Category, Cart, Order, OrderItem
from .forms import RegistrationForm, CustomLoginForm, CheckoutForm
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Cart, Order
from .forms import EditAccountForm
import random
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .forms import ForgotPasswordForm
from django.conf import settings
from datetime import timedelta
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import ForgotPasswordForm


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            # Redirect to 'next' if present, otherwise default to user page
            next_url = request.GET.get('next', 'user_page')  # Default to user_page if no 'next' is found
            return redirect(next_url)
        else:
            # Adding custom error messages if form is not valid
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


# Register View
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # Using email as username
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


# Home View
def home(request):
    categories = Category.objects.all()

    # Optionally, fetch some featured jewelry items, e.g., the latest or most popular
    featured_jewelry = Jewelry.objects.all().order_by('-created_at')[:6]  # Display the most recent 6 items

    # Pass categories and featured jewelry to the template
    return render(request, 'home/home.html', {
        'categories': categories,
        'featured_jewelry': featured_jewelry
    })


def about(request):
    return render(request, 'home/about.html')




@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the login page or any other page



@login_required
def user_view(request):
    # Fetch categories and jewelry as before
    categories = Category.objects.all()
    featured_jewelry = Jewelry.objects.all().order_by('-created_at')[:6]

    return render(request, 'user/user.html', {
        'categories': categories,
        'featured_jewelry': featured_jewelry
    })


# Category Items View
def category_items(request, category_name):
    category = get_object_or_404(Category, name=category_name)

    # Filter the jewelry items by the category
    jewelry_items = Jewelry.objects.filter(category=category)

    return render(request, 'category/category_items.html', {'jewelry_items': jewelry_items, 'category': category})


def product_detail(request, id):
    jewelry = get_object_or_404(Jewelry, id=id)
    jewelry_type = jewelry.__class__.__name__  # Get the model name as a string
    stock_range = range(1, jewelry.stock + 1)  # Generate a range from 1 to stock

    return render(request, 'category/product_detail.html', {
        'jewelry': jewelry,
        'jewelry_type': jewelry_type,
        'stock_range': stock_range,  # Pass the stock range to the template
    })


@login_required
def add_to_cart(request, jewelry_id):
    jewelry = get_object_or_404(Jewelry, id=jewelry_id)
    quantity = int(request.POST.get('quantity', 1))  # Default to 1 if no quantity is provided

    # Check if the item is already in the user's cart
    cart_item, created = Cart.objects.get_or_create(user=request.user, jewelry=jewelry)

    if not created:  # If the cart item exists, update its quantity
        cart_item.quantity += quantity
        cart_item.save()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    # Redirect to the cart view or wherever appropriate
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)  # Get all cart items for the logged-in user
    total = sum(item.get_total_price() for item in cart_items)  # Calculate the total price
    return render(request, 'cart/view_cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
        cart_item.delete()
        return redirect('view_cart')  # Redirect to the cart view after deletion
    except Cart.DoesNotExist:
        return redirect('view_cart')  # If the cart item doesn't exist, just go back to the cart page


# Update Cart Quantity (Increase/Decrease)
@transaction.atomic
def update_cart_quantity(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(Cart, id=item_id, user=request.user)
        action = request.POST.get("action")  # 'increase' or 'decrease'
        
        if action not in ["increase", "decrease"]:
            return JsonResponse({"success": False, "error": "Invalid action."}, status=400)

        try:
            if action == "increase":
                # Increase quantity if stock is available
                if item.jewelry.stock > item.quantity:  # Check if stock is available
                    item.quantity += 1
                    item.jewelry.stock -= 1
                    item.jewelry.save()
                    item.save()
                    return JsonResponse({
                        "success": True,
                        "quantity": item.quantity,
                        "total_price": item.get_total_price(),
                        "stock": item.jewelry.stock
                    })
                else:
                    return JsonResponse({
                        "success": False,
                        "error": "Not enough stock available."
                    }, status=400)

            elif action == "decrease":
                # Decrease quantity but ensure it doesn't go below 1
                if item.quantity > 1:
                    item.quantity -= 1
                    item.jewelry.stock += 1
                    item.jewelry.save()
                    item.save()
                    return JsonResponse({
                        "success": True,
                        "quantity": item.quantity,
                        "total_price": item.get_total_price(),
                        "stock": item.jewelry.stock
                    })
                else:
                    return JsonResponse({
                        "success": False,
                        "error": "Quantity cannot be less than 1."
                    }, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)



@login_required
def checkout(request):
    # Fetch items in the user's cart
    cart_items = Cart.objects.filter(user=request.user)
    
    # Check if the cart is empty
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('user_page')  # Redirect to the homepage or cart view

    cart_data = []
    total_price = 0

    # Calculate the total price for each cart item and overall total
    for item in cart_items:
        total_item_price = item.quantity * item.jewelry.price
        cart_data.append({
            'name': item.jewelry.name,
            'quantity': item.quantity,
            'price': item.jewelry.price,
            'total': total_item_price
        })
        total_price += total_item_price
        
        for item in cart_items:
            if item.jewelry.stock < item.quantity:
                messages.error(request, f"Not enough stock for {item.jewelry.name}. Available stock: {item.jewelry.stock}")
                return redirect('view_cart')  # Redirect back to the cart page

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Retrieve the selected payment method from the form
            payment_method = form.cleaned_data['payment_method']

            # Create a new order for the user
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                order_status='pending',
                payment_method=payment_method
            )

            # Add items to the order and update jewelry stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    jewelry=item.jewelry,
                    quantity=item.quantity,
                    price_per_item=item.jewelry.price
                )
                # Reduce stock for the jewelry
                item.jewelry.stock -= item.quantity
                item.jewelry.save()

            # Clear the cart after successful order placement
            cart_items.delete()

            # Redirect to the order success page
            return render(request, 'cart/order_confirmation.html')
        else:
            # If the form is invalid, show errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = CheckoutForm()

    return render(request, 'cart/checkout.html', {
        'cart_data': cart_data,
        'total_price': total_price,
        'form': form
    })

@login_required
def my_orders(request):
    # Get the filter option from the query parameters (default is None for all orders)
    order_status_filter = request.GET.get('status', None)

    # If filter is applied, filter the orders by status; otherwise fetch all orders
    if order_status_filter:
        my_orders = Order.objects.filter(user=request.user, order_status=order_status_filter)
    else:
        my_orders = Order.objects.filter(user=request.user)

    return render(request, 'user/my_orders.html', {
        'my_orders': my_orders,
        'order_status_filter': order_status_filter,  # To remember the filter in the template
    })



@login_required
def buy_now(request, jewelry_id, quantity):
    # Retrieve the jewelry item
    jewelry = get_object_or_404(Jewelry, id=jewelry_id)

    # Check if sufficient stock is available
    if jewelry.stock >= quantity:
        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=jewelry.price * quantity
        )

        # Create the order item
        OrderItem.objects.create(
            order=order,
            jewelry=jewelry,
            quantity=quantity,
            price_per_item=jewelry.price
        )

        # Reduce the stock for the jewelry
        try:
            jewelry.reduce_stock(quantity)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('product_detail', id=jewelry_id)

        # Redirect to the order confirmation page
        return redirect('order_confirmation', order_id=order.id)

    else:
        messages.error(request, "Insufficient stock available for this item.")
        return redirect('product_detail', id=jewelry_id)



def order_confirmation(request, order_id):
    # Get the order using order_id, if it exists
    order = get_object_or_404(Order, id=order_id)

    # Pass the order to the template
    return render(request, 'order/order_confirmation.html', {'order': order})


def shop(request):
    categories = Category.objects.all()

    # Optionally, fetch some featured jewelry items, e.g., the latest or most popular
    featured_jewelry = Jewelry.objects.all().order_by('-created_at')[:6]  # Display the most recent 6 items

    # Pass categories and featured jewelry to the template
    return render(request, 'user/shop.html', {
        'categories': categories,
        'featured_jewelry': featured_jewelry
    })


def home_shop(request):
    categories = Category.objects.all()

    # Optionally, fetch some featured jewelry items, e.g., the latest or most popular
    featured_jewelry = Jewelry.objects.all().order_by('-created_at')[:6]  # Display the most recent 6 items

    # Pass categories and featured jewelry to the template
    return render(request, 'home/home_shop.html', {
        'categories': categories,
        'featured_jewelry': featured_jewelry
    })




otp_store = {}

def generate_otp():
    """Generates a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                # Check if user exists
                user = User.objects.get(email=email)
                
                # Generate OTP and store it along with the expiration time
                otp = generate_otp()
                otp_store[email] = {
                    'otp': otp,
                    'expires_at': timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
                }

                # Send OTP to user's email
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'OTP sent to your email address. Please check your inbox.')
                return redirect('verify_otp', email=email)  # Redirect to OTP verification page
            except User.DoesNotExist:
                messages.error(request, 'This email is not registered. Please enter a valid email.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


def verify_otp(request, email):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if email in otp_store:
            otp_data = otp_store[email]
            # Check if OTP is expired
            if otp_data['expires_at'] > timezone.now():
                # Check if OTP matches
                if otp_entered == otp_data['otp']:
                    # OTP is valid
                    return redirect('reset_password', email=email)  # Redirect to password reset page
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
            else:
                messages.error(request, 'OTP has expired. Please request a new one.')
        else:
            messages.error(request, 'Invalid OTP request.')

    return render(request, 'accounts/verify_otp.html', {'email': email})



def reset_password(request, email):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            # Ensure the password is not empty
            if new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('login')  # Redirect to login page
            else:
                messages.error(request, 'Please enter a valid password.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    return render(request, 'accounts/reset_password.html', {'email': email})


@login_required
def my_account(request):
    return render(request, 'user/my_account.html', {'user': request.user})




@login_required
def edit_account(request):
    if request.method == 'POST':
        form = EditAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account details have been updated successfully.')
            return redirect('my_account')
    else:
        form = EditAccountForm(instance=request.user)

    return render(request, 'user/edit_account.html', {'form': form})
