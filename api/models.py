from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user for Role based use
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('delivery', 'Delivery Personnel'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class SellerProfile(models.Model):
    # One user(who is a seller) can only have one Seller Profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'seller'})
    company_name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # If category is deleted we still want the Product to show
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    # Only users with seller role are able to be displayed as a seller for the product
    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'seller'})
    posted_at = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True, default='')
    
    def __str__(self):
        return self.name

class SellerInventory(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'seller'})
    profile = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='inventory', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.seller.username

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'customer'})
    # auto_now_add=True: Sets the timestamp only once, on creation. 
    # Ideal for created_at or added_on fields.
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now=True: Updates the timestamp every time the object is saved. 
    # Ideal for updated_at or last_modified fields.
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

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

        if self.cart_items.count() == 0:
            raise ValueError("Cannot checkout: Cart is empty")

        # Create our order 
        order = Order.objects.create(
            customer=self.user,
            status='pending',
            total_price=self.total_price
        )
        
        # Create order items from cart items
        for item in self.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                purchase_price=item.product.price
            )
            
        # Create notification for the customer
        Notification.objects.create(
        user=self.user,
        message=f"Your order #{order.id} has been confirmed! Total: ${self.total_price}",
        seen=False
        )
        
        # Clear the cart
        self.cart_items.all().delete()
        self.total_price = 0
        self.save()

        return order

    def __str__(self):
        return self.user.username

# Each item in a cart
class CartItem(models.Model):
    # Referring to the Model by its string name so that we can have circular reference for 
    # total price
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

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


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(User, limit_choices_to={'role': 'customer'}, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

class Delivery(models.Model):
    # One order can only be delivered once
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(User, limit_choices_to={'role': 'delivery'},on_delete=models.CASCADE)
    # Choices are already declared in Order Model
    status = models.CharField(choices=Order.STATUS_CHOICES)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)