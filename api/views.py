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
from rest_framework import generics, parsers


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

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    
    # Override create to set seller as current user
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    # Override update to ensure only seller can update their own products
    def update(self, request, *args, **kwargs):
        product = self.get_object()
        if product.seller != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only update your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    # Override destroy to ensure only seller can delete their own products
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product.seller != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only delete your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    # Filter by seller
    @action(detail=False, methods=['get'], url_path='my-products')
    def my_products(self, request):
        if request.user.role != 'seller':
            return Response(
                {"error": "Only sellers can view their products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        products = Product.objects.filter(seller=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    # Update stock
    @action(detail=True, methods=['patch'], url_path='update-stock')
    def update_stock(self, request, pk=None):
        product = self.get_object()
        
        # Check permission
        if product.seller != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only update stock for your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {"error": "Quantity is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "Quantity must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.quantity = quantity
        product.save()
        
        return Response({
            "success": True,
            "message": f"Stock updated to {quantity}",
            "product": product.name,
            "quantity": product.quantity,
            "stock_status": product.stock_status
        })

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
                # 1. Get user's cart
                cart = Cart.objects.get(user=request.user)
                # 2. Get each item from the cart
                cart_items = cart.cart_items.select_related('product').all()
                
                # 3. Validate cart items
                if not cart_items.exists():
                    return Response({"error": "Cart is empty"}, status=400)
                
                # Check if all products are available and in stock
                total_amount = 0
                errors = []
                
                for item in cart_items:
                    # Check product availability
                    if not item.product.is_available:
                        errors.append(f"{item.product.name} is no longer available")
                        continue
                    
                    # Check stock quantity
                    if item.product.quantity < item.quantity:
                        errors.append(f"Not enough stock for {item.product.name}. Only {item.product.quantity} left")
                        continue
                    
                    # Calculate total amount
                    total_amount += item.product.price * item.quantity
                
                # If any errors, return them
                if errors:
                    return Response({"errors": errors}, status=400)
                
                # 4. Create the order
                order = Order.objects.create(
                    customer=request.user,
                    total_price=total_amount,
                    status='pending',
                )
                
                # 5. Convert cart items into order items and update product quantities
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        purchase_price=cart_item.product.price
                    )

                    # UPDATE: Reduce product quantity directly (no SellerInventory)
                    cart_item.product.quantity -= cart_item.quantity
                    
                    # If stock reaches 0, mark product as unavailable
                    if cart_item.product.quantity == 0:
                        cart_item.product.is_available = False
                    
                    cart_item.product.save()
                
                # 6. Clear the cart after successful checkout
                cart.cart_items.all().delete()
                cart.total_price = 0.00
                cart.save()
                
                # Return success response with order details
                return Response({
                    "success": True,
                    "message": "Checkout successful",
                    "order_id": order.id,
                    "order_code": order.order_code,
                    "total_amount": str(total_amount),
                    "status": order.status
                })

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
        except Exception as e:
            return Response({"error": f"Checkout failed: {str(e)}"}, status=500)
        
    # Add cart action
    @action(detail=False, methods=['post'], url_path='add-to-cart')
    def add_to_cart(self, request):
        """
        Add product to cart using product_code
        
        POST /api/cart/add-to-cart/
        
        Request Body:
        {
            "product_code": "ABC123", 
            "quantity": 2            
        }"""
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_code = serializer.validated_data['product_code']
        quantity = serializer.validated_data['quantity']
        
        try:
            with transaction.atomic():
                # Get product
                try:
                    product = Product.objects.get(product_code=product_code)
                except Product.DoesNotExist:
                    return Response(
                        {"error": f"Product with code '{product_code}' does not exist"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Check availability
                if not product.is_available:
                    return Response(
                        {"error": f"{product.name} is not available"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check stock
                if product.quantity < quantity:
                    return Response(
                        {"error": f"{product.name} only has {product.quantity} pieces left"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get or create cart
                cart, created = Cart.objects.get_or_create(
                    user=request.user,
                    defaults={'cart_code': generate_random_code()}
                )
                
                if created:
                    cart.total_price = 0.00
                    cart.save()
                
                # Check if product already in cart
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                
                if not item_created:
                    # Update existing cart item
                    new_quantity = cart_item.quantity + quantity
                    
                    # Check if new quantity exceeds stock
                    if product.quantity < new_quantity:
                        return Response(
                            {"error": f"Cannot add {quantity} more. {product.name} only has {product.quantity} pieces left"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    message = "Cart item quantity updated"
                else:
                    message = "Product added to cart"
                
                # Update cart total
                cart_items = CartItem.objects.filter(cart=cart)
                total = sum(item.product.price * item.quantity for item in cart_items)
                cart.total_price = total
                cart.save()
                
                return Response({
                    "success": True,
                    "message": message,
                    "cart_item_id": cart_item.id,
                    "product": product.name,
                    "product_code": product.product_code,
                    "quantity": cart_item.quantity,
                    "price_per_item": str(product.price),
                    "total_for_item": str(product.price * cart_item.quantity),
                    "cart_total": str(cart.total_price)
                })
                
        except Exception as e:
            return Response(
                {"error": f"Failed to add to cart: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['get'], url_path='my-cart')
    def my_cart(self, request):
        """
        Get current user's cart with all items
        
        GET /api/cart/my-cart/
        """
        try:
            cart = Cart.objects.get(user=request.user)
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            # Return empty cart if doesn't exist
            return Response({
                "user": request.user.id,
                "cart_items": [],
                "total_price": "0.00",
                "item_count": 0
            })

    @action(detail=False, methods=['post'], url_path='update-item')
    def update_cart_item(self, request):
        """
        Update quantity of a specific cart item
        
        POST /api/cart/update-item/
        
        Request Body:
        {
            "item_id": 1,           # CartItem ID
            "quantity": 3           # New quantity
        }"""
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        item_id = serializer.validated_data['item_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            with transaction.atomic():
                cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
                
                # Check if product is still available
                if not cart_item.product.is_available:
                    return Response({
                        "error": f"{cart_item.product.name} is no longer available"
                    }, status=400)
                
                # Check stock
                if cart_item.product.quantity < quantity:
                    return Response({
                        "error": f"Cannot update to {quantity}. {cart_item.product.name} only has {cart_item.product.quantity} left"
                    }, status=400)
                
                # Calculate price difference
                price_diff = (quantity - cart_item.quantity) * cart_item.product.price
                
                # Update cart item
                cart_item.quantity = quantity
                cart_item.save()
                
                # Update cart total
                cart = cart_item.cart
                cart.total_price += price_diff
                cart.save()
                
                return Response({
                    "success": True,
                    "message": "Cart item updated",
                    "quantity": cart_item.quantity,
                    "total_for_item": str(cart_item.product.price * cart_item.quantity),
                    "cart_total": str(cart.total_price)
                })
                
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)
        except Exception as e:
            return Response({"error": f"Failed to update cart: {str(e)}"}, status=500)

    @action(detail=False, methods=['delete'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_cart_item(self, request, item_id=None):
        """
        Remove specific item from cart
        
        DELETE /api/cart/remove-item/{item_id}/
        
        URL Parameter:
        - item_id: ID of the cart item to remove"""
        try:
            with transaction.atomic():
                cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
                cart = cart_item.cart
                
                # Calculate price to subtract
                price_to_subtract = cart_item.product.price * cart_item.quantity
                
                # Remove item
                cart_item.delete()
                
                # Update cart total
                cart.total_price -= price_to_subtract
                if cart.total_price < 0:
                    cart.total_price = 0.00
                cart.save()
                
                return Response({
                    "success": True,
                    "message": "Item removed from cart",
                    "cart_total": str(cart.total_price),
                    "remaining_items": cart.cart_items.count()
                })
                
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)
        except Exception as e:
            return Response({"error": f"Failed to remove item: {str(e)}"}, status=500)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        """
        Remove all items from cart
        
        DELETE /api/cart/clear/t"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.cart_items.all().delete()
            cart.total_price = 0.00
            cart.save()
            
            return Response({
                "success": True,
                "message": "Cart cleared successfully"
            })
            
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
        except Exception as e:
            return Response({"error": f"Failed to clear cart: {str(e)}"}, status=500)
        
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