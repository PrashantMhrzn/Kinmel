from rest_framework import serializers as s
from .models import *

class SellerInventorySerializer(s.ModelSerializer):
    product = s.SlugRelatedField(slug_field='name', read_only=True)
    seller = s.CharField(source='seller.username', read_only=True)

    class Meta:
        model = SellerInventory 
        exclude = ['profile']

class SellerProfileSerializer(s.ModelSerializer):
    # We don't want to change the seller so we use charfield
    user = s.CharField(source='user.username', read_only=True)
    # Since seller profile and seller inventory aren't directly related
    # We have to manually define how inventory is calculated or displayed
    inventory = s.SerializerMethodField() # Look for a method get_inventory to get the value to display

    class Meta:
        model = SellerProfile
        fields = ['id', 'user', 'company_name', 'verified', 'inventory']

    def get_inventory(self, obj):
        # Fetch inventory of the same seller
        return SellerInventorySerializer(SellerInventory.objects.filter(seller=obj.user), many=True).data

class CategorySerializer(s.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(s.ModelSerializer):
    posted_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'seller', 'posted_at']

class CartItemSerializer(s.ModelSerializer):
    product = s.SlugRelatedField(slug_field='name', queryset=Product.objects.all())
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartSerializer(s.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    user = s.CharField(source='user.username', read_only=True)
    total_price = s.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'total_price', 'cart_items']

# class CartItemSerializer(s.ModelSerializer):
#     class Meta:
#         model = CartItem
class OrderItemSerializer(s.ModelSerializer):
    product = s.SlugRelatedField(slug_field='name', queryset=Product.objects.all())
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'purchase_price']

class OrderSerializer(s.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = s.CharField(source='customer.username', read_only=True)
    # Display the time in a readable format
    created_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_price','status' ,'created_at', 'updated_at', 'items' ]

class DeliverySerializer(s.ModelSerializer):
    delivery_person = s.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    shipped_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    delivered_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Delivery
        fields = ['id', 'order', 'delivery_person','status' ,'shipped_at', 'delivered_at' ]

class NotificationSerializer(s.ModelSerializer):
    created_at = s.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    user = s.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message','seen' ,'created_at' ]




