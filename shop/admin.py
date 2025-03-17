from django.contrib import admin
from .models import Jewelry, Category, Ring, Earring, Bracelet, Necklace
from .models import Order

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display category name in the list view
    search_fields = ('name',)  # Allow searching by category name

# Register Jewelry model
@admin.register(Jewelry)
class JewelryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'category', 'created_at')  # Fields to display in the list view
    search_fields = ('name', 'description')  # Allow searching by name and description
    list_filter = ('category',)  # Add a filter for category

# Register Ring model
@admin.register(Ring)
class RingAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'material', 'price', 'category', 'created_at')
    search_fields = ('name', 'size', 'material')
    list_filter = ('category',)  # Add a filter for category

# Register Earring model
@admin.register(Earring)
class EarringAdmin(admin.ModelAdmin):
    list_display = ('name', 'length', 'style', 'price', 'category', 'created_at')
    search_fields = ('name', 'length', 'style')
    list_filter = ('category',)  # Add a filter for category

# Register Bracelet model
@admin.register(Bracelet)
class BraceletAdmin(admin.ModelAdmin):
    list_display = ('name', 'material', 'clasp_type', 'price', 'category', 'created_at')
    search_fields = ('name', 'material', 'clasp_type')
    list_filter = ('category',)  # Add a filter for category

# Register Necklace model
@admin.register(Necklace)
class NecklaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'length', 'pendant_type', 'price', 'category', 'created_at')
    search_fields = ('name', 'length', 'pendant_type')
    list_filter = ('category',)  # Add a filter for category

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'order_status', 'created_at', 'updated_at')  # Ensure these fields exist
    list_editable = ('order_status',)  # Allows you to edit the order status directly in the list view
    search_fields = ('user__username', 'user__email')  # Search orders by username or email
    list_filter = ('order_status', 'created_at')  # Filter by status and creation date

admin.site.register(Order, OrderAdmin)






# Define a custom admin class for the User model
class UserAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ('username', 'first_name', 'last_name', 'email', 'date_joined', 'is_active', 'is_staff')

    # Add filtering options to the admin view
    list_filter = ('is_active', 'is_staff', 'date_joined')

    # Add search functionality in the admin view
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Allow actions like deleting users
    actions = ['delete_selected']

    # Optionally, you can customize the form for User editing, but this is for viewing/deleting.

# Register the User model with the custom UserAdmin class
admin.site.unregister(User)  # Unregister the default User admin
admin.site.register(User, UserAdmin)
