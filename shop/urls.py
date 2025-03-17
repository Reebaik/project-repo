from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView


urlpatterns = [
    path('', views.home, name='home'),
    path('user_page/', views.user_view, name='user_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('category/<str:category_name>/', views.category_items, name='category_items'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:jewelry_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),  # Added checkout route
    path('my-orders/', views.my_orders, name='my_orders'),
    path('buy-now/<int:jewelry_id>/<int:quantity>/', views.buy_now, name='buy_now'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('shop/', views.shop, name='shop'),
    path('home-shop/', views.home_shop, name='home_shop'),
    path('about/', views.about, name='about'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/<str:email>/', views.verify_otp, name='verify_otp'),
    path('reset-password/<str:email>/', views.reset_password, name='reset_password'),
    path('my_account/', views.my_account, name='my_account'),
    path('edit_account/', views.edit_account, name='edit_account'),
    path(
        'change_password/',
        PasswordChangeView.as_view(template_name='user/change_password.html'),
        name='change_password'
    ),
    path(
        'password_change_done/',
        PasswordChangeDoneView.as_view(template_name='user/password_change_done.html'),
        name='password_change_done'
    ),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
