from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .permissions import *
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.db import transaction


class SellerProfileView(ModelViewSet):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer
    # Permissions
    permission_classes = [IsSellerOrReadOnly] # Everybody(including unauthenticated) can read, only seller can edit

class CategoryView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Filtering by name
    search_fields = ['name']
    permission_classes = [ReadOnly | IsAdmin] # Everybdoy can read, only admin can edit

class ProductView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Filtering data
    filterset_fields = ['category', 'price'] # Filter with values
    search_fields = ['name', 'category__name']  # Filter by searching
    ordering_fields = ['price', 'posted_at'] # Sort the filter
    permission_classes = [ProductOwnerOrReadOnly]

class SellerInventoryView(ModelViewSet):
    queryset = SellerInventory.objects.all()
    serializer_class = SellerInventorySerializer
    # Filtering
    filterset_fields = ['product__category', 'stock_quantity']
    search_fields = ['product__name']
    ordering_fields = ['stock_quantity']
    permission_classes = [IsAuthenticated, IsSellerOrReadOnly] # Everybody(excluding unauthorized) can view, but only seller can edit


class CartView(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    # /api/cart/checkout
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """Checkout cart and create order"""
        try:
            with transaction.atomic():
                # 1. get users Cart
                cart = Cart.objects.get(user=request.user)
                # 2. get each item from the cart
                cart_items = cart.cart_items.select_related('product').all()
                # 3. validate cart items
                # check if there are items in the cart
                if not cart_items.exists():
                    return Response({"error": "Cart is empty"})
                
                # check if the stock is available
                total_amount = 0
                inventory_dict = {}
                
                for item in cart_items:
                    try:
                        inventory = SellerInventory.objects.get(seller=item.product.seller, product=item.product)
                        inventory_dict[item.product.id] = inventory
                    except SellerInventory.DoesNotExist:
                        return Response({"error": f"{item.product.name} is no longer available in inventory"})
                    
                    if not item.product.is_available:
                        return Response({"error": f"{item.product.name} is no longer available"})
                    
                    if inventory.stock_quantity < item.quantity:
                        return Response({"error": f"Not enough stock for {item.product.name} stock left {inventory.stock_quantity}"})
                    
                    # calculate the total amount from the products
                    total_amount += item.product.price * item.quantity

                # 4. create the order
                order = Order.objects.create(
                    customer = request.user,
                    total_price = total_amount,
                    status = 'pending',
                )
                # 5. convert cart items into orderitems
                for cart_item in cart_items:
                    inventory = inventory_dict[cart_item.product.id]
                    
                    OrderItem.objects.create(
                        order = order,
                        product = cart_item.product,
                        quantity = cart_item.quantity,
                        purchase_price = cart_item.product.price
                    )

                    # Update seller inventory stock
                    inventory.stock_quantity -= cart_item.quantity
                    inventory.save()
                    
                    # If stock reaches 0, mark product as unavailable
                    if inventory.stock_quantity == 0:
                        cart_item.product.is_available = False
                        cart_item.product.save()
                
                # 6. Clear the cart after successful checkout
                cart.cart_items.all().delete()
                cart.total_price = 0.00
                cart.save()
                
                # Return success response with order details
                return Response({
                    "message": "Checkout successful",
                    "order_id": order.id,
                    "total_amount": total_amount
                })

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"})
        except  Exception as e:
            return Response({"error": f"Checkout failed: {str(e)}"})
    
class OrderView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Filtering
    filterset_fields = ['customer', 'status']
    search_fields = ['customer__username']
    ordering_fields = ['created_at', 'total_price']

    permission_classes = [OrderPermission]

    def get_queryset(self):
        user = self.request.user
        # Admins can see all orders
        if user.is_staff:
            return Order.objects.all()
        # Customers can only see their orders
        return Order.objects.filter(customer=user)
        

class DeliveryView(ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated, DeliveryPermission]
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Delivery.objects.all()
        # Delivery personnel can only see their own deliveries
        return Delivery.objects.filter(delivery_person=user)
   

class NotificationView(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    # @action(detail=True, methods=['patch'])
    # def mark_as_read(self, request, pk=None):
    #     notification = self.get_object()
    #     notification.seen = True
    #     notification.save()
    #     return Response({"status": "marked as read"})