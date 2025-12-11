from rest_framework import serializers
from .models import *


# User serializer for API responses
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'address']
        
class SellerInventorySerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field='name', read_only=True)
    seller = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = SellerInventory 
        exclude = ['profile']

class SellerProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    inventory = serializers.SerializerMethodField()

    class Meta:
        model = SellerProfile
        fields = ['id', 'user', 'company_name', 'verified', 'inventory']

    def get_inventory(self, obj):
        return SellerInventorySerializer(
            SellerInventory.objects.filter(seller=obj.user), 
            many=True
        ).data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    posted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all())
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'seller', 'posted_at', 'image_url', 'product_code']

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
    quantity = serializers.IntegerField(min_value=1, default=1)
