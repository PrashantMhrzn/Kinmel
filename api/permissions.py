from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'seller'

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'

class IsDelivery(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'delivery'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class IsOwnerOrReadOnly(BasePermission):
    """Only owner can edit; everyone can read"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(obj, 'user') and obj.user == request.user

class IsSellerOrReadOnly(BasePermission):
    """Only seller can edit, all can read"""
    def has_permission(self, request, view):
        # Always allow GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'seller'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and hasattr(obj, 'user') and obj.user == request.user

class ProductOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only for anyone
        if request.method in SAFE_METHODS:
            return True
        # Only allow write (POST, PUT, DELETE) if user is authenticated and a seller
        return request.user.is_authenticated and request.user.role == 'seller'

    def has_object_permission(self, request, view, obj):
        # Allow read-only for anyone
        if request.method in SAFE_METHODS:
            return True
        # Only allow modifying the product if the user is the seller who added it
        return request.user.is_authenticated and obj.seller == request.user

class CartOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        # Must be logged in and either admin or customer
        return user.is_authenticated and user.role in ['admin', 'customer']

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin can access all carts
        if user.is_staff:
            return True

        # Customer can access their own cart only
        return obj.customer == user

class OrderPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False 

        if request.method in SAFE_METHODS:
            return user.role in ['admin', 'seller', 'customer', 'delivery']

        return user.is_staff

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

class DeliveryPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        # Only allow authenticated admin or delivery personnel
        return user.is_authenticated and user.role in ['admin', 'delivery']

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Admin can access all deliveries
        if user.role == 'admin':
            return True
        # Delivery personnel can only access their own deliveries
        return obj.delivery_person == user