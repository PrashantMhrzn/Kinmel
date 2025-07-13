from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

# Creating Router
router = DefaultRouter()
router.register(r'seller_profile', SellerProfileView)
router.register(r'seller_inventory', SellerInventoryView)
router.register(r'category', CategoryView)
router.register(r'product', ProductView)
router.register(r'cart', CartView)
router.register(r'order', OrderView)
router.register(r'delivery', DeliveryView)
router.register(r'notification', NotificationView)

urlpatterns = [
    # path('/', ),
    # path('', include(router.urls)),
] + router.urls