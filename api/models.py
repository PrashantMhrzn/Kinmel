from django.db import models as m
from django.contrib.auth.models import AbstractUser


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
    user = m.OneToOneField(User, on_delete=m.CASCADE)
    company_name = m.CharField()
    verified = m.BooleanField(default=False)

class Category(m.Model):
    name = m.CharField()
    description = m.TextField()

class Product(m.Model):
    name = m.CharField()
    description = m.TextField()
    price = m.PositiveIntegerField()
    category = m.ForeignKey(Category, on_delete=m.PROTECT)
    seller = m.ForeignKey(User, on_delete=m.CASCADE)

class SellerInventory(m.Model):
    seller = m.OneToOneField(User, on_delete=m.CASCADE)
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    stock_quantity = m.IntegerField()

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
    customer = m.ForeignKey(User, on_delete=m.CASCADE)
    total_price = m.IntegerField()
    status = m.CharField()
    created_at = m.DateTimeField()
    updated_at = m.DateTimeField()

class OrderItem(m.Model):
    order = m.ForeignKey(Order, on_delete=m.CASCADE, related_name='items')
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    quantity = m.PositiveIntegerField()
    purchase_price = m.IntegerField()

class Delivery(m.Model):
    order = m.OneToOneField(Order, on_delete=m.CASCADE)
    delivery_person = m.ForeignKey(User, on_delete=m.CASCADE)
    status = m.CharField()
    shipped_at = m.DateTimeField(null=True, blank=True)
    delivered_at = m.DateTimeField(null=True, blank=True)

class Notification(m.Model):
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    mesage = m.TextField()
    seen = m.BooleanField(default=False)
    created_at = m.DateTimeField()