from rest_framework import serializers as s
from .models import *

class SellerProfileSerializer(s.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['id', 'user', 'company_name', 'verified']

class CategorySerializer(s.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(s.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'seller', 'posted_at']

class SellerInventorySerializer(s.ModelSerializer):
    class Meta:
        model = SellerInventory
        fields = ['id', 'seller', 'profile', 'product', 'stock_quantity']

class CartSerializer(s.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'total_price']

# class CartItemSerializer(s.ModelSerializer):
#     class Meta:
#         model = CartItem

class OrderSerializer(s.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_price','status' ,'created_at', 'updated_at' ]

class DeliverySerializer(s.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id', 'order', 'delivery_person','status' ,'shipped_at', 'delivered_at' ]

class NotificationSerializer(s.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message','seen' ,'created_at' ]




