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
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return user.role in ['customer', 'admin']
        return user.role == 'customer' and obj.customer == user

class OrderPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Only allow read access to specific roles if the user is authenticated
        if request.method in SAFE_METHODS:
            return user.is_authenticated and user.role in ['admin', 'seller', 'customer', 'delivery']

        # Only admin can edit
        return user.is_authenticated and user.is_staff

class DeliveryPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return user.role in ['admin', 'seller', 'customer', 'delivery']
        return user.role in ['admin', 'delivery']