from rest_framework import serializers
from .models import *


# User serializer for API responses
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'address']
        

class SellerProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    inventory = serializers.SerializerMethodField()

    class Meta:
        model = SellerProfile
        fields = ['id', 'user', 'company_name', 'verified', 'inventory']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    # Remove in_stock and stock_status if you don't need them
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'quantity',
            'category', 'category_name', 'seller', 'seller_name',
            'image', 'is_available', 'product_code', 'posted_at'
            # Removed: 'stock_status', 'in_stock'
        ]
        read_only_fields = ['seller', 'product_code', 'posted_at']
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'total_price', 'created_at', 'cart_items', 'cart_code']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'purchase_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'total_price', 'status', 'created_at', 'items', 'order_code']

class DeliverySerializer(serializers.ModelSerializer):
    delivery_person = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    shipped_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    delivered_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = Delivery
        fields = ['id', 'order', 'delivery_person', 'status', 'shipped_at', 'delivered_at']

class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'seen', 'created_at']

class AddToCartSerializer(serializers.Serializer):
    product_code = serializers.CharField(max_length=6)
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
class UpdateCartItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_code', 'product_price', 'quantity', 'total_price']
    
    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_name', 'cart_items', 'total_price', 'item_count', 'created_at', 'updated_at']
    
    def get_item_count(self, obj):
        return obj.cart_items.count()