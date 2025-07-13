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

    def __str__(self):
        return self.user.username

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

    def __str__(self):
        return self.name

class SellerInventory(m.Model):
    seller = m.OneToOneField(User, on_delete=m.CASCADE, limit_choices_to={'role': 'seller'})
    profile = m.OneToOneField(SellerProfile, on_delete=m.CASCADE, null=True, blank=True)
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    stock_quantity = m.PositiveIntegerField()

    def __str__(self):
        return self.seller.username

class Cart(m.Model):
    user = m.OneToOneField(User, on_delete=m.CASCADE, limit_choices_to={'role': 'customer'})
    # auto_now_add=True: Sets the timestamp only once, on creation. 
    # Ideal for created_at or added_on fields.
    created_at = m.DateTimeField(auto_now_add=True)
    # auto_now=True: Updates the timestamp every time the object is saved. 
    # Ideal for updated_at or last_modified fields.
    updated_at = m.DateTimeField(auto_now=True)
    total_price = m.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    # Each time an item is added to this cart, we take its price and add it to the total 
    # so that we have a total price of all items in the cart
    def update_total_price(self):
        total = 0
        for item in self.cart_items.all():
            if item.product and item.quantity:
                total += item.product.price * item.quantity
                
        self.total_price = total
        self.save(update_fields=['total_price'])
        
    def checkout(self):
        # We import order and orderitem here because we need it for the checkout funtion
        # We cannot import it at the top because those models haven't been declared yet
        # This method only runs when called and not on load so by then all models are loaded
        from .models import Order, OrderItem 

        if self.items.count() == 0:
            raise ValueError("Cart is empty.")

        order = Order.objects.create(
            customer=self.customer,
            status='pending',
            total_price=0.0
        )

        total = 0
        for item in self.cart_items.all():
            subtotal = item.product.price * item.quantity
            OrderItem.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                purchase_price = item.product.price
            )
            total += subtotal

        order.total_price = total
        order.save()

        self.items.all().delete()
        self.total_price = 0
        self.save()

        return order

    def __str__(self):
        return self.user.username

# Each item in a cart
class CartItem(m.Model):
    # Referring to the Model by its string name so that we can have circular reference for 
    # total price
    cart = m.ForeignKey('Cart', on_delete=m.CASCADE, related_name='cart_items')
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    quantity = m.PositiveIntegerField(default=1)

    # Modifying the save function so that when a item is saved, it also updates the cart's 
    # total price
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cart.update_total_price()

    # Before deleting an item, save reference and updated cart total afterwards
    def delete(self, *args, **kwargs):
        cart = self.cart
        super().delete(*args, **kwargs)
        cart.update_total_price()
    
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

    def __str__(self):
        return f"Order #{self.pk} by {self.customer.username}"

class OrderItem(m.Model):
    order = m.ForeignKey(Order, on_delete=m.CASCADE, related_name='Oitems')
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    quantity = m.PositiveIntegerField()
    purchase_price = m.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

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