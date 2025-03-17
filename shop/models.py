from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal  # Add this line at the top of the models.py file

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category_image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

class Jewelry(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='jewelries')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='jewelry_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.stock < 0:
            self.stock = 0
        super().save(*args, **kwargs)

    def reduce_stock(self, quantity):
        """
        Reduce the stock of the jewelry by the specified quantity.
        If there is insufficient stock, raise an error.
        """
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Not enough stock available for this item.")

# Ring subclass
class Ring(Jewelry):
    size = models.CharField(max_length=10)  # Specific attribute for Rings
    material = models.CharField(max_length=50)  # Material type for Rings

# Earring subclass
class Earring(Jewelry):
    length = models.FloatField()  # Specific attribute for Earrings
    style = models.CharField(max_length=50)  # Style of the earrings

# Bracelet subclass
class Bracelet(Jewelry):
    material = models.CharField(max_length=50)  # Material type for Bracelets
    clasp_type = models.CharField(max_length=50)  # Clasp type for Bracelets

# Necklace subclass
class Necklace(Jewelry):
    length = models.FloatField()  # Specific attribute for Necklaces
    pendant_type = models.CharField(max_length=50)  # Type of pendant for Necklaces

# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jewelry = models.ForeignKey(Jewelry, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.jewelry.name} (x{self.quantity}) - {self.user.username}"

    def get_total_price(self):
        return self.jewelry.price * self.quantity

# Order Model
class Order(models.Model):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED ,'Confirmed'),
        (CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ])

    def __str__(self):
        return f"Order {self.id} - {self.order_status}"

    def update_stock(self):
        """
        Update the stock of items in the jewelry after the order is placed.
        This function should be called when the order is confirmed or placed.
        """
        for order_item in self.orderitems.all():
            jewelry = order_item.jewelry
            jewelry.reduce_stock(order_item.quantity)

    def get_order_items(self):
        """
        Returns all items associated with this order.
        This assumes you have a through model for the many-to-many relationship.
        """
        return self.orderitems.all()

    @property
    def get_total_amount(self):
        """
        Calculate the total price of the order based on the order items.
        """
        total = 0
        for item in self.get_order_items():
            total += item.total_price
        return total

# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='orderitems', on_delete=models.CASCADE)
    jewelry = models.ForeignKey(Jewelry, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.price_per_item * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.jewelry.name} (Total: {self.total_price})"



