from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet

class SellerProfileView(ModelViewSet):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer

class CategoryView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SellerInventoryView(ModelViewSet):
    queryset = SellerInventory.objects.all()
    serializer_class = SellerInventorySerializer

class CartView(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class OrderView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class DeliveryView(ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

class NotificationView(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer