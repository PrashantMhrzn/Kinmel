from django.db import models as m
from django.contrib.auth.models import AbstractUser

# Custom user for Role based use
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('delivery', 'Delivery Personnel'),
    )
    role = m.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = m.CharField(max_length=15, blank=True, null=True)
    address = m.TextField(blank=True, null=True)

class SellerProfile(m.Model):
    # One user(who is a seller) can only have one Seller Profile
    user = m.OneToOneField(User, on_delete=m.CASCADE, limit_choices_to={'role': 'seller'})
    company_name = m.CharField(max_length=100)
    verified = m.BooleanField(default=False)

class Category(m.Model):
    name = m.CharField(max_length=100, unique=True)
    description = m.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(m.Model):
    name = m.CharField(max_length=100)
    description = m.TextField()
    price = m.DecimalField(max_digits=10, decimal_places=2)
    # If category is deleted we still want the Product to show
    category = m.ForeignKey(Category, on_delete=m.SET_NULL, null=True)
    # Only users with seller role are able to be displayed as a seller for the product
    seller = m.ForeignKey(User, on_delete=m.CASCADE, limit_choices_to={'role': 'seller'})
    posted_at = m.DateTimeField(auto_now_add=True)

class SellerInventory(m.Model):
    seller = m.OneToOneField(User, on_delete=m.CASCADE, limit_choices_to={'role': 'seller'})
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    stock_quantity = m.PositiveIntegerField()

class Cart(m.Model):
    user = m.OneToOneField(User, on_delete=m.CASCADE, limit_choices_to={'role': 'customer'})
    # auto_now_add=True: Sets the timestamp only once, on creation. 
    # Ideal for created_at or added_on fields.
    created_at = m.DateTimeField(auto_now_add=True)
    # auto_now=True: Updates the timestamp every time the object is saved. 
    # Ideal for updated_at or last_modified fields.
    updated_at = m.DateTimeField(auto_now=True)

# Each item in a cart
class CartItems(m.Model):
    cart = m.ForeignKey(Cart, on_delete=m.CASCADE, related_name='cart_items')
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    quantity = m.PositiveIntegerField(default=1)

    # To stop duplicate items in the same cart
    class Meta:
        unique_together = ('cart', 'product')

class Order(m.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    customer = m.ForeignKey(User, limit_choices_to={'role': 'customer'}, on_delete=m.CASCADE)
    total_price = m.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = m.CharField(choices=STATUS_CHOICES, default='pending')
    created_at = m.DateTimeField(auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)

class OrderItem(m.Model):
    order = m.ForeignKey(Order, on_delete=m.CASCADE, related_name='items')
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    quantity = m.PositiveIntegerField()
    purchase_price = m.DecimalField(max_digits=10, decimal_places=2)

class Delivery(m.Model):
    # One order can only be delivered once
    order = m.OneToOneField(Order, on_delete=m.CASCADE)
    delivery_person = m.ForeignKey(User, limit_choices_to={'role': 'delivery'},on_delete=m.CASCADE)
    # Choices are already declared in Order Model
    status = m.CharField(choices=Order.STATUS_CHOICES)
    shipped_at = m.DateTimeField(null=True, blank=True)
    delivered_at = m.DateTimeField(null=True, blank=True)

class Notification(m.Model):
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    mesage = m.TextField()
    seen = m.BooleanField(default=False)
    created_at = m.DateTimeField(auto_now_add=True)