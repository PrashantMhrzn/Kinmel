from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .permissions import *
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

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
    def get_queryset(self):
        user = self.request.user
        # Admins can see all carts
        if user.is_staff:
            return Cart.objects.all()

        # Customers can only see their own cart
        return Cart.objects.filter(user=user)
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, CartOwnerPermission]

    # This creates a custom endpoint orders/checkout/
    @action(detail=False, methods=['post'], url_path='checkout', url_name='checkout')
    def checkout(self, request):
        user = request.user
        
        # Verify user is a customer
        if user.role != 'customer':
            return Response(
                {"error": "Only customers can checkout"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            order = cart.checkout()
            serializer = OrderSerializer(order)
            return Response(
                {
                    "message": "Checkout successful!",
                    "order": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    

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
    permission_classes = [ReadOnly]